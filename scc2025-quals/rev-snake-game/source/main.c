#include <ncurses.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define WIDTH 40
#define HEIGHT 20
#define INITIAL_DELAY 100
#define SPEED_INCREASE 0.9

#define UP 0
#define RIGHT 1
#define DOWN 2
#define LEFT 3

#define SNAKE_HEAD_PAIR 1
#define SNAKE_BODY_PAIR 2
#define FOOD_PAIR 3
#define WALL_PAIR 4
#define WIN_PAIR 5

typedef struct {
  int x;
  int y;
} Position;

int snake_x[WIDTH * HEIGHT];
int snake_y[WIDTH * HEIGHT];
int prev_snake_x[WIDTH * HEIGHT];
int prev_snake_y[WIDTH * HEIGHT];
int prev_length;
int snake_length;
int direction;
Position food_position;

char flag[30] = {20,  165, 74,  8,   100, 177, 126, 135, 186, 50,
                 157, 159, 223, 10,  205, 33,  67,  134, 71,  41,
                 238, 208, 148, 208, 182, 218, 206, 67,  211, 223};
#define POINTS_TO_WIN sizeof(flag)

Position positions[POINTS_TO_WIN];
int score;
int game_over;
int max_y, max_x;
double delay;

void initialize_ncurses();
void initialize_game();
void draw_initial_game();
void draw_updates();
void process_input();
void update_game();
void place_food();
void game_loop();
void show_game_over();
void show_win_screen();
void collect();

void initialize_ncurses() {
  initscr();
  cbreak();
  keypad(stdscr, TRUE);
  noecho();
  curs_set(0);

  getmaxyx(stdscr, max_y, max_x);

  if (max_y < HEIGHT + 5 || max_x < WIDTH + 2) {
    printw("Terminal window too small. Minimum size: %dx%d\n", WIDTH + 2,
           HEIGHT + 5);
    getch();
    endwin();
    exit(1);
  }

  if (has_colors()) {
    start_color();
    init_pair(SNAKE_HEAD_PAIR, COLOR_WHITE, COLOR_RED);
    init_pair(SNAKE_BODY_PAIR, COLOR_BLACK, COLOR_GREEN);
    init_pair(FOOD_PAIR, COLOR_BLACK, COLOR_YELLOW);
    init_pair(WALL_PAIR, COLOR_BLACK, COLOR_BLUE);
    init_pair(WIN_PAIR, COLOR_BLACK, COLOR_CYAN);
  }
}

void initialize_game() {
  snake_length = 1;
  snake_x[0] = WIDTH / 2;
  snake_y[0] = HEIGHT / 2;

  prev_length = 0;

  direction = RIGHT;

  score = 0;

  game_over = 0;

  delay = INITIAL_DELAY;

  for (int i = 0; i < POINTS_TO_WIN; i++) {
    int curr = rand() % (WIDTH * HEIGHT);
    positions[i].x = curr % WIDTH;
    positions[i].y = curr / WIDTH;
    // printf("%d\n", curr);
  }
  //   usleep(10000000);

  place_food();
}

void draw_initial_game() {
  clear();

  attron(COLOR_PAIR(WALL_PAIR));
  for (int i = 0; i < WIDTH + 2; i++) {
    mvaddch(0, i, '#');
    mvaddch(HEIGHT + 1, i, '#');
  }
  for (int i = 0; i < HEIGHT + 2; i++) {
    mvaddch(i, 0, '#');
    mvaddch(i, WIDTH + 1, '#');
  }
  attroff(COLOR_PAIR(WALL_PAIR));

  mvprintw(HEIGHT + 3, 1, "Score: %d / %d", score, POINTS_TO_WIN);
  mvprintw(HEIGHT + 4, 1, "Points needed to win: %d", POINTS_TO_WIN - score);
  mvprintw(HEIGHT + 5, 1, "Use arrow keys to move. Press q to quit.");

  draw_updates();
}

void draw_updates() {
  // Clear old snake tail if needed
  if (prev_length > 0) {
    for (int i = 0; i < prev_length; i++) {
      bool still_exists = false;
      for (int j = 0; j < snake_length; j++) {
        if (prev_snake_x[i] == snake_x[j] && prev_snake_y[i] == snake_y[j]) {
          still_exists = true;
          break;
        }
      }
      if (!still_exists) {
        mvaddch(prev_snake_y[i] + 1, prev_snake_x[i] + 1, ' ');
      }
    }
  }

  // Draw snake body
  attron(COLOR_PAIR(SNAKE_BODY_PAIR));
  for (int i = 1; i < snake_length; i++) {
    mvaddch(snake_y[i] + 1, snake_x[i] + 1, ' ');
  }
  attroff(COLOR_PAIR(SNAKE_BODY_PAIR));

  // Draw snake head
  attron(COLOR_PAIR(SNAKE_HEAD_PAIR));
  mvaddch(snake_y[0] + 1, snake_x[0] + 1, ' ');
  attroff(COLOR_PAIR(SNAKE_HEAD_PAIR));

  // Draw food
  attron(COLOR_PAIR(FOOD_PAIR));
  mvaddch(food_position.y + 1, food_position.x + 1, ' ');
  attroff(COLOR_PAIR(FOOD_PAIR));

  // Update score display if it changed
  mvprintw(HEIGHT + 3, 1, "Score: %d / %d", score, POINTS_TO_WIN);
  mvprintw(HEIGHT + 4, 1, "Points needed to win: %d", POINTS_TO_WIN - score);

  // Store the current state for the next update
  for (int i = 0; i < snake_length; i++) {
    prev_snake_x[i] = snake_x[i];
    prev_snake_y[i] = snake_y[i];
  }
  prev_length = snake_length;

  refresh();
}

void process_input() {
  int key = getch();

  if (key != ERR) {
    switch (key) {
    // case 'q':
    // case 'Q':
    //   for (int i = 0; i < POINTS_TO_WIN; i++)
    //     collect();
    //   break;
    case KEY_UP:
      if (direction != DOWN)
        direction = UP;
      break;
    case KEY_RIGHT:
      if (direction != LEFT)
        direction = RIGHT;
      break;
    case KEY_DOWN:
      if (direction != UP)
        direction = DOWN;
      break;
    case KEY_LEFT:
      if (direction != RIGHT)
        direction = LEFT;
      break;
    case 'q':
    case 'Q':
      game_over = 1;
      break;
    }
  }
}

void collect() {
  score++;

  delay *= SPEED_INCREASE;

  snake_x[snake_length] = snake_x[snake_length - 1];
  snake_y[snake_length] = snake_y[snake_length - 1];
  snake_length++;

  flag[snake_length - 2] ^=
      (positions[snake_length - 2].x + positions[snake_length - 2].y * WIDTH) &
      0xFF;

  place_food();
}

void update_game() {
  int old_tail_x = snake_x[snake_length - 1];
  int old_tail_y = snake_y[snake_length - 1];

  for (int i = snake_length - 1; i > 0; i--) {
    snake_x[i] = snake_x[i - 1];
    snake_y[i] = snake_y[i - 1];
  }

  switch (direction) {
  case UP:
    snake_y[0]--;
    break;
  case RIGHT:
    snake_x[0]++;
    break;
  case DOWN:
    snake_y[0]++;
    break;
  case LEFT:
    snake_x[0]--;
    break;
  }

  // Check collision with walls
  if (snake_x[0] < 0 || snake_x[0] >= WIDTH || snake_y[0] < 0 ||
      snake_y[0] >= HEIGHT) {
    game_over = 1;
    return;
  }

  // Check collision with self
  for (int i = 1; i < snake_length; i++) {
    if (snake_x[0] == snake_x[i] && snake_y[0] == snake_y[i]) {
      game_over = 1;
      return;
    }
  }

  // Check collision with food
  if (snake_x[0] == food_position.x && snake_y[0] == food_position.y) {
    collect();
  }
}

void place_food() { food_position = positions[snake_length]; }

void show_game_over() {
  clear();
  mvprintw(max_y / 2 - 2, max_x / 2 - 5, "GAME OVER!");
  mvprintw(max_y / 2, max_x / 2 - 10, "Your final score: %d / %d", score,
           POINTS_TO_WIN);
  mvprintw(max_y / 2 + 2, max_x / 2 - 14, "Press any key to exit the game.");
  refresh();
  timeout(-1); // Wait indefinitely for a keypress
  getch();
}

void show_win_screen() {
  clear();

  attron(COLOR_PAIR(WIN_PAIR) | A_BOLD);
  mvprintw(max_y / 2 - 4, max_x / 2 - 10, "Congratulations!");
  attroff(COLOR_PAIR(WIN_PAIR) | A_BOLD);

  mvprintw(max_y / 2 - 2, max_x / 2 - 13, "You've collected all %d points!",
           POINTS_TO_WIN);

  attron(A_BOLD);
  mvprintw(max_y / 2, max_x / 2 - strlen(flag) / 2, "Flag: %s", flag);
  attroff(A_BOLD);

  mvprintw(max_y / 2 + 3, max_x / 2 - 14, "Press any key to exit the game.");

  refresh();
  timeout(-1);
  getch();
}

void game_loop() {
  draw_initial_game();

  timeout((int)delay);

  while (!game_over) {
    process_input();
    update_game();
    draw_updates();
    if (score >= POINTS_TO_WIN) {
      show_win_screen();
      return;
    }
    timeout((int)delay);
  }
  show_game_over();
}

int main() {
  srand(0);

  initialize_ncurses();
  initialize_game();
  game_loop();
  endwin();

  return 0;
}