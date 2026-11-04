import os
from pwn import *
from collections import deque
import heapq

# Adapted from the challenge's own checker/solve.py (author-provided).
#
# Each of the 100 levels is a freshly generated maze; levels 1-49 are plain
# BFS shortest-path mazes, and from level 50 onward a "minotaur" chases the
# player by always stepping toward them along the tree of floor tiles
# (computed via an LCA/binary-lifting walk), with single-use "passage" tiles
# that can shortcut around it. MinotaurSolver below models the minotaur's
# exact pursuit rule and runs a Dijkstra-style search over (position,
# minotaur position, used-passages bitmask) state so the chosen path is
# provably survivable, retrying with newly-discovered "bad" passages
# excluded if a search turns out to use one more than once.
HOST = os.environ.get("SERVICE_LABYRINTH_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_LABYRINTH_SHELL_PORT", "1337"))

WALL = 0
FLOOR = 1
PASS = 2

DIRS = [
    (1, 0, 's'),
    (-1, 0, 'w'),
    (0, 1, 'd'),
    (0, -1, 'a'),
]
CH2D = {ch: (dx, dy) for dx, dy, ch in DIRS}


def parse_board(io, n):
    board = []
    for _ in range(n):
        line = io.recvline().decode('utf-8', 'ignore')
        row = line[:n]
        if len(row) < n:
            row = row.ljust(n, '#')
        board.append(row)
    return board


def shortest_path_no_minotaur(board, n):
    start = (1, 1)
    goal = (n - 2, n - 2)

    q = deque([start])
    parent = {start: None}

    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break

        for dx, dy, ch in DIRS:
            nx, ny = x + dx, y + dy
            if board[nx][ny] == '#':
                continue
            if (nx, ny) in parent:
                continue
            parent[(nx, ny)] = (x, y, ch)
            q.append((nx, ny))

    if goal not in parent:
        raise RuntimeError('no path found on non-minotaur level')

    path = []
    cur = goal
    while cur != start:
        px, py, ch = parent[cur]
        path.append(ch)
        cur = (px, py)

    return ''.join(reversed(path))


class MinotaurSolver:
    def __init__(self, board):
        self.n = len(board)
        self.lab = [[self._cell(ch) for ch in row] for row in board]

        self.floor_nodes = []
        self.pass_nodes = []
        self.floor_id = {}
        self.pass_id = {}

        for i in range(self.n):
            for j in range(self.n):
                cell = self.lab[i][j]
                if cell == FLOOR:
                    self.floor_id[(i, j)] = len(self.floor_nodes)
                    self.floor_nodes.append((i, j))
                elif cell == PASS:
                    self.pass_id[(i, j)] = len(self.pass_nodes)
                    self.pass_nodes.append((i, j))

        self.F = len(self.floor_nodes)
        self.coords = self.floor_nodes + self.pass_nodes
        self.pid = {}

        for coord, idx in self.floor_id.items():
            self.pid[coord] = idx
        for coord, idx in self.pass_id.items():
            self.pid[coord] = self.F + idx

        self.start = self.floor_id[(1, 1)]
        self.goal = self.floor_id[(self.n - 2, self.n - 2)]
        self.root = self.goal
        self.pass_bit = {self.F + idx: idx for idx in range(len(self.pass_nodes))}

        self.padj = [[] for _ in range(len(self.coords))]
        for node, (i, j) in enumerate(self.coords):
            for dx, dy, ch in DIRS:
                ni, nj = i + dx, j + dy
                if 0 <= ni < self.n and 0 <= nj < self.n and self.lab[ni][nj] != WALL:
                    self.padj[node].append((self.pid[(ni, nj)], ch))

        self._build_tree_helpers()
        self.dist = self._goal_distances()

    @staticmethod
    def _cell(ch):
        if ch == '#':
            return WALL
        if ch == '.':
            return PASS
        # ' ', '@', '$', 'P', 'M' are all floor-like for the solver.
        return FLOOR

    def _build_tree_helpers(self):
        adj = [[] for _ in range(self.F)]
        for idx, (i, j) in enumerate(self.floor_nodes):
            for dx, dy, _ in DIRS:
                ni, nj = i + dx, j + dy
                other = self.floor_id.get((ni, nj))
                if other is not None:
                    adj[idx].append(other)

        self.LOG = (self.F + 1).bit_length()
        self.up = [[self.root] * self.F for _ in range(self.LOG)]
        self.depth = [0] * self.F
        self.tin = [0] * self.F
        self.tout = [0] * self.F

        timer = 0
        stack = [(self.root, self.root, 0)]  # node, parent, 0=enter/1=exit
        while stack:
            v, p, state = stack.pop()
            if state == 0:
                self.up[0][v] = p
                for k in range(1, self.LOG):
                    self.up[k][v] = self.up[k - 1][self.up[k - 1][v]]
                self.tin[v] = timer
                timer += 1
                stack.append((v, p, 1))
                for u in adj[v]:
                    if u == p:
                        continue
                    self.depth[u] = self.depth[v] + 1
                    stack.append((u, v, 0))
            else:
                self.tout[v] = timer
                timer += 1

    def _goal_distances(self):
        dist = [10 ** 18] * len(self.coords)
        q = deque([self.goal])
        dist[self.goal] = 0

        while q:
            v = q.popleft()
            nd = dist[v] + 1
            for u, _ in self.padj[v]:
                if dist[u] > nd:
                    dist[u] = nd
                    q.append(u)

        return dist

    def is_floor(self, node):
        return node < self.F

    def is_ancestor(self, a, b):
        return self.tin[a] <= self.tin[b] and self.tout[b] <= self.tout[a]

    def lca(self, a, b):
        if self.is_ancestor(a, b):
            return a
        if self.is_ancestor(b, a):
            return b

        x = a
        for k in range(self.LOG - 1, -1, -1):
            ux = self.up[k][x]
            if not self.is_ancestor(ux, b):
                x = ux
        return self.up[0][x]

    def kth_ancestor(self, v, k):
        bit = 0
        while k:
            if k & 1:
                v = self.up[bit][v]
            k >>= 1
            bit += 1
        return v

    def step_toward(self, m, p):
        if m == p:
            return m

        l = self.lca(m, p)
        if l != m:
            return self.up[0][m]

        # m is an ancestor of p, so move one step downward toward p.
        return self.kth_ancestor(p, self.depth[p] - self.depth[m] - 1)

    def simulate(self, path):
        p = self.start
        m = self.root
        used = 0

        for ch in path:
            if p == self.goal:
                return True, 'win', None

            x, y = self.coords[p]
            dx, dy = CH2D[ch]
            np = self.pid.get((x + dx, y + dy))
            if np is None:
                return False, 'wall', None

            bit = self.pass_bit.get(np)
            if bit is not None:
                if (used >> bit) & 1:
                    return False, 'usedpass', np
                used |= 1 << bit
            else:
                m = self.step_toward(m, np)
                if m == np:
                    return False, 'caught', None

            p = np

        return (p == self.goal), 'eof', None

    def search(self, tracked_passes, max_states=2_000_000):
        # Only passages that actually caused trouble are tracked in the state.
        # This keeps the search small while still enforcing single-use exactly.
        tracked_index = {node: i for i, node in enumerate(sorted(tracked_passes))}

        start_state = (self.start, self.root, 0)
        pq = [(self.dist[self.start], 0, start_state)]
        best = {start_state: 0}
        parent = {start_state: None}
        seen = 0

        while pq and seen < max_states:
            _, cost, state = heapq.heappop(pq)
            if cost != best.get(state):
                continue
            seen += 1

            p, m, used = state
            if p == self.goal:
                path = []
                cur = state
                while parent[cur] is not None:
                    prev, ch = parent[cur]
                    path.append(ch)
                    cur = prev
                path.reverse()
                return ''.join(path), seen

            for np, ch in self.padj[p]:
                nm = m
                nused = used

                if self.is_floor(np):
                    nm = self.step_toward(m, np)
                    if nm == np:
                        continue
                else:
                    idx = tracked_index.get(np)
                    if idx is not None:
                        bit = 1 << idx
                        if used & bit:
                            continue
                        nused = used | bit

                nxt = (np, nm, nused)
                nc = cost + 1
                if nc < best.get(nxt, 10 ** 18):
                    best[nxt] = nc
                    parent[nxt] = (state, ch)
                    heapq.heappush(pq, (nc + self.dist[np], nc, nxt))

        return None, seen

    def solve(self):
        tracked = set()
        for _ in range(64):
            path, _ = self.search(tracked)
            if path is None:
                raise RuntimeError('no winning path found')

            ok, reason, bad_pass = self.simulate(path)
            if ok:
                return path

            if reason == 'usedpass':
                tracked.add(bad_pass)
                continue

            raise RuntimeError(f'solver failed: {reason}')

        raise RuntimeError('too many retry iterations')


def solve_level(io, level):
    n = 2 * level + 3
    io.recvuntil(f'Level: {level}\n'.encode())
    board = parse_board(io, n)

    if level < 50:
        path = shortest_path_no_minotaur(board, n)
    else:
        path = MinotaurSolver(board).solve()

    io.sendlineafter(b'Move (WASD): ', path.encode())
    log.info(f'level {level}: {len(path)} moves')


def main():
    context.log_level = 'info'

    io = remote(HOST, PORT)

    io.sendlineafter(b'to begin.\n\n', b'')

    for level in range(1, 101):
        solve_level(io, level)

    try:
        final = io.recvuntil(b'Freedom was never given. It was earned.\n\n', timeout=15)
    except EOFError:
        final = io.clean(timeout=1)
    io.close()

    output = final.decode('utf-8', 'ignore')
    print(output)

    flag_env = os.environ.get('flag_flag')
    if flag_env and flag_env not in output:
        raise SystemExit(f'flag mismatch: expected {flag_env!r} to be in output')


if __name__ == '__main__':
    main()
