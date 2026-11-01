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

const char* questions[] = {
    "What randomizes memory addresses to prevent predictability?",
    "What makes executables independent of memory address?",
    "What refers to small code chunks in a binary?",
    "Does the `read` function require a newline at the end of input?",
    "What vulnerability reveals secret memory addresses?"
};

const char* answers[] = {
    "ASLR", "PIE", "Gadgets", "No", "Memory Leak"
};

void list_files() {
    system("ls");
}

void banner() {
    puts(COLOR_RED"\t______________________  _________\n"
         "\t___  __ )__  ____/_  / / /_  ___/\n"
         COLOR_BLUE"\t__  __  |_  __/  _  / / /_____ \\ \n"
         "\t_  /_/ /_  /___  / /_/ / ____/ / \n"
         COLOR_WHITE"\t/_____/ /_____/  \\____/  /____/  \n"
         "                                     LEVEL 2\n"
        COLOR_RED"Binary"COLOR_BLUE" Exploitation Unit"COLOR_WHITE" of Serbia\n"COLOR_RESET);
    puts("Answer the questions to continue to the next level");
}

bool question(int i) {
    char ans[128] = {0};
    char yesno;

    printf("[?] Q%d: %s\n", i+1, questions[i]);
    while(true) {
        printf("Answer> ");
        read(0, ans, 152);
        ans[strcspn(ans, "\n")] = '\0';

        printf("Is your answer '%s'? [y/n]> ", ans);
        yesno = getchar();
        getchar();
        if(yesno == 'y') break;
    }

    return strcasecmp(ans, answers[i]) == 0;
}

int main() {
    char buf[128] = {0};
    int cnt = 0;

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    banner();
    for(int i=0;i<5;i++) {
        if(question(i)) {
            puts(COLOR_GREEN "[+] Correct\n" COLOR_RESET);
            cnt++;
        }
        else {
            puts(COLOR_RED "[-] Incorrect!\n" COLOR_RESET);
        }
    }

    if(cnt == 5) {
        printf("Any last comment> ");
        gets(buf);
        puts(COLOR_RED "[!] You failed anyway!" COLOR_RESET);
    } else {
        puts(COLOR_RED "[-] You didn't answer all questions correctly!" COLOR_RESET);
    }
    return 0;
}