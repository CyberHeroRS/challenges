#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define WIDTH 19
#define HEIGHT 14

char maze[HEIGHT][WIDTH + 1] = {
    "###################",
    "#P          #######",
    "### ##### #    ####",
    "### #   # ####    #",
    "### ### # #### ## #",
    "#   ###        ## #",
    "#####   #####  #  #",
    "##### #########  ##",
    "#     ###       ###",
    "# ########## ######",
    "# ###    ### ######",
    "# ###### ###    E##",
    "#  #### ##### #####",
    "###################"
};
int playerX = 1, playerY = 1;

void printMaze() {
    for (int i = 0; i < HEIGHT; i++) {
        printf("%s\n", maze[i]);
    }
}

void movePlayer(char direction) {
    int newX = playerX, newY = playerY;

    if (direction == 'w') newY--;
    if (direction == 's') newY++;
    if (direction == 'a') newX--;
    if (direction == 'd') newX++;

    if (newY < 0 || newY >= HEIGHT || newX < 0 || newX >= WIDTH) {
        return;
    }

    if (maze[newY][newX] == ' ' || maze[newY][newX] == 'E') {
        maze[playerY][playerX] = ' ';
        playerX = newX;
        playerY = newY;
        if (maze[newY][newX] == ' ') {
            maze[playerY][playerX] = 'P';
        }
    }
}

void printScoreboard(const char *playerName, double timeTaken) {
    printf("==========================\n");
    printf("|  GREAT HEIST           |\n");
    printf("|  SIMULATORINATOR       |\n");
    printf("|  SCOREBOARD            |\n");
    printf("==========================\n");
    printf("| Player | Time\n");
    printf("==========================\n");
    printf("| ???    | 0.1\n");
    printf("--------------------------\n");
    printf("| ");
    printf(playerName);
    printf(" | %.2f\n", timeTaken);
    printf("--------------------------\n");
    printf("| MAN     | 10.5\n");
    printf("--------------------------\n");
    printf("| SOM     | 49.19\n");
    printf("--------------------------\n");
    printf("| VUC     | 105.6\n");
    printf("==========================\n");
}

char secret_message[0x100] = {};

void __attribute__((constructor)) initialize () {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    if (setenv("TERM", "xterm-256color", 1) != 0) {
        perror("setenv");
    }
    const char* fg = getenv("FLAG");
    if (fg) {
        strncpy(secret_message, getenv("FLAG"), 0x100);
    }
}

int main() {
    char input=0, playerName[20] = {};
    time_t startTime=0, endTime=0;

    printf("To prepare you for the upcoming heist, you have\n");
    printf("been tasked to train using the \"GREAT HEIST SIMULATORINATOR\".\n");
    printf("Supposedly, it tests more than just your pathfinding...\n\n");

    printf("Press Enter to Start");
    fflush(stdout);
    getchar();
    
    time(&startTime);
    
    while (1) {
        fflush(stdout);
        system("clear");
        printMaze();

        if (maze[playerY][playerX] == 'E') {
            time(&endTime);
            double timeTaken = difftime(endTime, startTime);

            printf("Congratulations, you exited the maze in %.2f seconds.\n", timeTaken);
            printf("Would you like to add your time to the scoreboard? [y/n]");
            fflush(stdout);
            input = getchar();
            getchar();
            if (input == 'y') {
                printf("Enter your name: ");
                scanf("%19s", playerName);
                printScoreboard(playerName, timeTaken);
            } else {
                printf("Alright.");
            }
            break;
        }

        printf("Use w, a, s, d to move: ");
        fflush(stdout);
        input = getchar();
        getchar();
        movePlayer(input);
    }

    return 0;
}

