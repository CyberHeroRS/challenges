#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CARD_MIN 1
#define CARD_MAX 13

int draw_card() {
    return (rand() % (CARD_MAX - CARD_MIN + 1)) + CARD_MIN;
}

char inside_sleeve[0x100] = {};

void __attribute__((constructor)) _() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    if (setenv("TERM", "xterm-256color", 1) != 0) {
        perror("setenv");
    }
    const char* fg = getenv("FLAG");
    if (fg) {
        strncpy(inside_sleeve, fg, 0x100);
    }
}

void game_over(){
    #define COLOR_RED "\e[0;31m"
    #define COLOR_RESET "\e[0m"

    printf("- It seems this has been a waste of my time.\n\n");
    printf(COLOR_RED "\t*You are shot from behind, dying instantly.*\n\n" COLOR_RESET);
    exit(1);
}

int main() {
    int current_card, next_card = -1;
    char choice;

    srand(time(NULL)); 

    puts("*You sit at a small round table. The lights dim.\nAt the opposite side of the table sits a hooded man with a deck of cards.\nThe deck looks unusually large.*");
    puts("\n- Let's see if you are worthy.\n");
    puts("*He shuffles the deck and hands you a card: there is no suite, it only says \"5\".*\n");

    current_card = 5;

    for(int i = 0; i < 200; ++i) {
        puts("- Higher, or lower?\n");
        printf("+ [h/l]: ");

        choice = getchar();
        getchar();

        do {
            next_card = draw_card();
        } while(next_card == current_card);

        if (choice == 'h') {
            puts("\n*He draws another card, looks at it, and places it face down.*\n");
            if (next_card > current_card) {
                puts("- Correct.\n\n*He sets the card aside*\n");
            } else {
                game_over();
            }
        } else if (choice == 'l') {
            puts("\n*He draws another card, looks at it, and places it face down.*\n");
            if (next_card < current_card) {
                puts("- Correct.\n*He sets the card aside*\n");
            } else {
                game_over();
            }
        } else {
            puts("\n- You think you're funny?\n");
            game_over();
        }

        current_card = next_card;
    }

    puts("- Alright. You pass, here.");
    printf("*He takes a piece of paper from inside his sleeve and hands it to you.\nIt says: %s*", inside_sleeve);

    return 0;
}
