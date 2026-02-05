import random, os

def dijkstra(start, end, graph):
    vertex_vals, edge_vals = graph
    visited = set()
    queue = {start: (0, [start])}

    while queue:
        curr_node = min(queue, key=lambda x: queue.get(x)[0])
        curr_dist, curr_path = queue.pop(curr_node)
        visited.add(curr_node)
        if curr_node == end:
            return curr_dist, curr_path

        for next in vertex_vals[curr_node]:
            if next[0] not in visited:
                new_dist = curr_dist + edge_vals[next[0]] * next[1]
                if next[0] not in queue or new_dist < queue[next[0]][0]:
                    queue[next[0]] = (new_dist, curr_path + [next[0]])
    return 0, []

def pprint(vertex_vals, path):
    vx = [[v[0] for v in vv] for vv in vertex_vals]
    out = ""
    for i in range(len(path) - 1):
        out += str(vx[path[i]].index(path[i + 1]))
    return out + "f"

N = 100

def random_graph():
    edge_vals = random.sample(range(1,1000), k=N)
    vertex_vals = []

    for i in range(N):
        if i > 6:
            next = random.sample(range(max(i-10,0), min(i+10,N)), k=random.randint(1,3)) + random.sample(range(i), k=random.randint(3,7))
        else:
            next = random.sample(range(i+1,i+20), k=random.randint(3,7))
        next = set(next) - {i}
        weights = random.sample(range(2,2*len(next)), k=len(next))
        vertex_vals.append([(n, w) for n,w in zip(next, weights)])
    return vertex_vals, edge_vals
    
bestl = 0
path = []
while len(path) < 40:
    vertex_vals, edge_vals = random_graph()
    TARGET, path = dijkstra(0, N-1, (vertex_vals, edge_vals))

print(f"vertex_vals = {vertex_vals}")
print(f"edge_vals = {edge_vals}")
print(f"path = {path}")
print(pprint(vertex_vals, path))

vertex_vals[-1].append((-1, TARGET))

code = """
#include <iostream>
#include <fstream>

#define ull unsigned long long

void printFlag() {
    std::ifstream file("flag.txt");
    std::string line;
    std::getline(file, line);
    std::cout << line << std::endl;
    exit(0);
}

class Node {
    private:
        ull val;
    public:
        ~Node() {}
        Node(ull val) : val(val) {}
        ull getVal() { return val; }
};

class Vertex: public Node {
    public:
        Vertex(ull val) : Node(val) {}
        virtual Vertex* handle() = 0;
};

class Edge: public Node {
    public:
        Edge(ull val) : Node(val) {}
        virtual Vertex* next(ull curr) = 0;
};
"""

for i,e in enumerate(edge_vals):
    code += f"""class E{i}: public Edge {{
    private: ull getX() {{ return {e}; }}
    public:
        E{i}(ull val) : Edge(val) {{}}
        Vertex *next(ull curr) override;
}};
"""
    
for i,v in enumerate(vertex_vals):
    code += f"class V{i}: public Vertex, "
    code += ", ".join([f"E{e}" for e,x in v if e != -1])
    code += f"""{{
    public:
        V{i}(ull val) : Vertex(val), """
    code += ", ".join([f"E{e}({x})" for e,x in v if e != -1])
    code += f"""{{}}
    Vertex *handle() {{
        Edge *e;
        switch (getchar()) {{
    """
    for j, (e,x) in enumerate(v):
        if e == -1:
            code += f"""case 'f': if (static_cast<Vertex*>(this)->getVal() == {TARGET}) printFlag();"""
        else:
            code += f"""case '{j}': e = static_cast<E{e}*>(this);break;"""
    code += """default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};"""
    
for i in range(N):
    code += f"""Vertex* E{i}::next(ull curr) {{ return new V{i}(curr + this->getVal() * this->getX()); }}"""

code += """int main() {
    Vertex* v = new V0(0);
    while (true) {
        v = v->handle();
    }
}"""

with open("src.cpp", "w") as f:
    f.write(code)

os.system("g++ -O0 -s src.cpp -o is_this_java")
