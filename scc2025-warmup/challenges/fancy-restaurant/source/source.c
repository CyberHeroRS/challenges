#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

void banner() {
    puts("╔══════════════════════════════════════════════╗");
    puts("║         WELCOME TO THE FANCY RESTAURANT      ║");
    puts("║   Access is allowed only to elegant people   ║");
    puts("╚══════════════════════════════════════════════╝");
}

uint8_t weight = 80, energy = 5;

void print_flag() {
    char* flag = getenv("FLAG");

    if(flag) {
        printf("%s\n", flag);
    }
}

int menu() {
    int choice;

    printf("* Energy: %hhu\n", energy);
    printf("* Weight: %hhu\n", weight);
    puts("1) Try to enter the restaurant");
    puts("2) Eat something");
    puts("3) Go jogging");
    puts("4) Give up");
    printf("Enter your choice> ");
    scanf("%d", &choice);

    return choice;
}

int main() {
    int choice;

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    banner();
    while(true) {
        choice = menu();
        switch(choice) {
            case 1:
                if(weight < 65) {
                    puts("* Monsieur, you may now enter the restaurant.");
                    puts("You found a piece of paper on the table with the following message:");
                    print_flag();
                }
                else {
                    puts("* Monsieur, sorry, but you are not elegant enough.");
                }
                break;
            case 2:
                if(energy < 5) {
                    puts("You ate something.");
                    energy = 5;
                    weight += 5;
                } else {
                    puts("You are not hungry.");
                }
                break;
            case 3:
                if(energy > 1) {
                    puts("You lost 1 kilogram.");
                    energy -= 2;
                    weight -= 1;
                } else {
                    puts("You are exhausted.");
                }
                break;
            case 4:
                exit(0);
            default:
                puts("Unknown choice.");
                break;
        }
        puts("");
    }
    return 0;
}
