#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>

#include <unistd.h>

#define COLOR_RED "\e[0;31m"
#define COLOR_BLUE "\e[0;34m"
#define COLOR_WHITE "\e[1;37m"
#define COLOR_RESET "\e[0m"
#define COLOR_GREEN "\e[1;32m"

void win() {
    printf(COLOR_GREEN "[+] You passed LEVEL 1! Congratulations!\nHere is your reward: %s\n" COLOR_RESET, getenv("FLAG"));
}

const char* questions[] = {
    "What does binary exploitation target?",
    "Where is the return address of a function stored?",
    "Where are local variables, like buffers, typically stored?",
    "Is using `gets()` considered safe?",
    "What is the vulnerability called when input exceeds buffer capacity?"
};

const char* answers[] = {
    "Memory", "Stack", "Stack", "No", "Buffer Overflow"
};

void banner() {
    puts(COLOR_RED"\t______________________  _________\n"
         "\t___  __ )__  ____/_  / / /_  ___/\n"
         COLOR_BLUE"\t__  __  |_  __/  _  / / /_____ \\ \n"
         "\t_  /_/ /_  /___  / /_/ / ____/ / \n"
         COLOR_WHITE"\t/_____/ /_____/  \\____/  /____/  \n"
         "                                     LEVEL 1\n"
        COLOR_RED"Binary"COLOR_BLUE" Exploitation Unit"COLOR_WHITE" of Serbia\n"COLOR_RESET);
    puts("Answer the questions to continue to the next level");
}

bool question(int i) {
    char ans[128] = {0};

    printf("[?] Q%d: %s\n", i+1, questions[i]);
    printf("Answer> ");
    read(0, ans, 128);
    ans[strcspn(ans, "\n")] = '\0';

    return strcasecmp(ans, answers[i]) == 0;
}

int main() {
    char buf[128] = {0};

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    banner();
    for(int i=0;i<5;i++) {
        if(question(i)) {
            puts(COLOR_GREEN "[+] Correct\n" COLOR_RESET);
        }
        else {
            puts(COLOR_RED "[-] Incorrect! You failed!\n" COLOR_RESET);
            return 1;
        }
    }

    printf("Any last comment> ");
    gets(buf);
    puts(COLOR_RED "[!] You failed anyway!" COLOR_RESET);
    return 0;
}