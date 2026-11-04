#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <queue>
#include <chrono>
#include <thread>
#include <fstream>

enum class Field {
    WALL,
    FLOOR,
    PASS
};

typedef std::vector<std::vector<Field>> Labyrinth;

static std::random_device rd;
static std::mt19937 gen(rd());

/* ================= TERMINAL CLEAR ================= */

inline void clear_screen() {
    std::cout << "\033[2J\033[H";
}

/* ================= PERFECT LABYRINTH CORE ================= */

void carve(int x, int y, Labyrinth& lab, int n) {
    lab[x][y] = Field::FLOOR;

    std::vector<std::pair<int,int>> dirs = {
        {2,0}, {-2,0}, {0,2}, {0,-2}
    };

    std::shuffle(dirs.begin(), dirs.end(), gen);

    for (auto [dx,dy] : dirs) {
        int nx = x + dx;
        int ny = y + dy;

        if (nx <= 0 || ny <= 0 || nx >= n-1 || ny >= n-1)
            continue;

        if (lab[nx][ny] == Field::WALL) {
            lab[x + dx/2][y + dy/2] = Field::FLOOR;
            carve(nx, ny, lab, n);
        }
    }
}

/* ================= ADD PASSAGES AFTER PERFECT TREE ================= */

void add_passages(Labyrinth& lab, int n, double probability = 0.06) {
    std::uniform_real_distribution<> dis(0.0,1.0);

    for (int i = 1; i < n-1; ++i) {
        for (int j = 1; j < n-1; ++j) {

            if (lab[i][j] != Field::WALL)
                continue;

            if (lab[i][j-1] == Field::FLOOR &&
                lab[i][j+1] == Field::FLOOR &&
                dis(gen) < probability)
                lab[i][j] = Field::PASS;

            if (lab[i-1][j] == Field::FLOOR &&
                lab[i+1][j] == Field::FLOOR &&
                dis(gen) < probability)
                lab[i][j] = Field::PASS;
        }
    }
}

Labyrinth generate_labyrinth(int n) {
    if (n % 2 == 0) n--;

    Labyrinth lab(n, std::vector<Field>(n, Field::WALL));

    carve(1,1,lab,n);

    lab[n-2][n-2] = Field::FLOOR;

    add_passages(lab, n, 0.06);

    return lab;
}

void start_banner() {
    clear_screen();
    std::cout << R"(

██╗      █████╗ ██████╗ ██╗   ██╗██████╗ ██╗███╗   ██╗████████╗██╗  ██╗
██║     ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██║████╗  ██║╚══██╔══╝██║  ██║
██║     ███████║██████╔╝ ╚████╔╝ ██████╔╝██║██╔██╗ ██║   ██║   ███████║
██║     ██╔══██║██╔══██╗  ╚██╔╝  ██╔══██╗██║██║╚██╗██║   ██║   ██╔══██║
███████╗██║  ██║██████╔╝   ██║   ██║  ██║██║██║ ╚████║   ██║   ██║  ██║
╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝

                LABYRINTH OF THE MINOTAUR

Symbols:
  @  - Start
  $  - Exit
  #  - Wall
     - Floor (unique solution path)
  .  - Passage (optional shortcut, collapses after use)
  P  - Player
  M  - Minotaur (appears from level 25+)

Only one true path exists using FLOOR tiles.
Passages create risky shortcuts.

Press Enter to begin.
)" << "\n";
}

void death_banner() {
    clear_screen();
    std::cout << R"(

██████╗  █████╗ ███╗   ███╗███████╗
██╔══██╗██╔══██╗████╗ ████║██╔════╝
██████╔╝███████║██╔████╔██║█████╗
██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

        YOU WERE CAUGHT
)" << "\n";
}

void print_labyrinth(const Labyrinth& lab,
                     int px, int py,
                     int mx, int my,
                     bool minotaur_active) {

    int n = lab.size();

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {

            if (i == px && j == py)
                std::cout << "P";
            else if (minotaur_active && i == mx && j == my)
                std::cout << "M";
            else if (i == 1 && j == 1)
                std::cout << "@";
            else if (i == n-2 && j == n-2)
                std::cout << "$";
            else {
                switch (lab[i][j]) {
                    case Field::WALL:  std::cout << "#"; break;
                    case Field::FLOOR: std::cout << " "; break;
                    case Field::PASS:  std::cout << "."; break;
                }
            }
        }
        std::cout << "\n";
    }
}

std::pair<int,int> minotaur_move(
    const Labyrinth& lab,
    int mx, int my,
    int px, int py) {

    int n = lab.size();

    std::queue<std::pair<int,int>> q;
    std::vector<std::vector<bool>> visited(n, std::vector<bool>(n,false));
    std::vector<std::vector<std::pair<int,int>>> parent(
        n, std::vector<std::pair<int,int>>(n, {-1,-1}));

    q.push({mx,my});
    visited[mx][my] = true;

    int dirs[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};

    while (!q.empty()) {
        auto [x,y] = q.front(); q.pop();

        if (x == px && y == py)
            break;

        for (auto& d : dirs) {
            int nx = x + d[0];
            int ny = y + d[1];

            if (nx < 0 || ny < 0 || nx >= n || ny >= n)
                continue;

            if (!visited[nx][ny] &&
                lab[nx][ny] == Field::FLOOR) {

                visited[nx][ny] = true;
                parent[nx][ny] = {x,y};
                q.push({nx,ny});
            }
        }
    }

    if (!visited[px][py])
        return {mx,my};

    std::pair<int,int> step = {px,py};
    while (parent[step.first][step.second] != std::make_pair(mx,my))
        step = parent[step.first][step.second];

    return step;
}

int main() {

    start_banner();
    std::cin.get();

    for (int level = 1; level <= 100; ++level) {

        int size = 5 + (level-1)*2;
        Labyrinth lab = generate_labyrinth(size);

        int px = 1, py = 1;
        int mx = size-2, my = size-2;

        bool minotaur_active = (level >= 50);

        while (true) {

            clear_screen();
            std::cout << "Level: " << level << "\n";
            print_labyrinth(lab, px, py, mx, my, minotaur_active);

            if (px == size-2 && py == size-2) {
                std::this_thread::sleep_for(std::chrono::milliseconds(600));
                break;
            }

            char move;
            std::cout << "Move (WASD): ";
            std::cin >> move;

            int nx = px;
            int ny = py;

            if (move == 'w' || move == 'W') nx--;
            if (move == 's' || move == 'S') nx++;
            if (move == 'a' || move == 'A') ny--;
            if (move == 'd' || move == 'D') ny++;

            if (lab[nx][ny] == Field::FLOOR ||
                lab[nx][ny] == Field::PASS) {

                if (lab[nx][ny] == Field::PASS)
                    lab[nx][ny] = Field::WALL;

                px = nx;
                py = ny;
            }

            if (minotaur_active) {
                auto next = minotaur_move(lab,mx,my,px,py);
                mx = next.first;
                my = next.second;

                if (mx == px && my == py) {
                    death_banner();
                    return 0;
                }
            }
        }
    }

    clear_screen();

    std::ifstream flag_file("flag.txt");
    std::string flag;

    if (flag_file.good()) {
        std::getline(flag_file, flag);
    } else {
        flag = "SCC{missing_flag_file}";
    }

    std::cout << R"(

██╗   ██╗ ██████╗ ██╗   ██╗    ███████╗███████╗ ██████╗ █████╗ ██████╗ ███████╗
╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝
 ╚████╔╝ ██║   ██║██║   ██║    █████╗  ███████╗██║     ███████║██████╔╝█████╗
  ╚██╔╝  ██║   ██║██║   ██║    ██╔══╝  ╚════██║██║     ██╔══██║██╔═══╝ ██╔══╝
   ██║   ╚██████╔╝╚██████╔╝    ███████╗███████║╚██████╗██║  ██║██║     ███████╗
   ╚═╝    ╚═════╝  ╚═════╝     ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚══════╝

You have conquered all 100 labyrinths.
The Minotaur lies defeated.
The stone doors open slowly...

Your reward awaits:

)";

    std::cout << "\n    " << flag << "\n\n";
    std::cout << "Freedom was never given. It was earned.\n\n";
    return 0;
}