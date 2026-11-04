#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>

#include <unistd.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <stddef.h>
#include <fcntl.h>

#define COLOR_RED "\e[0;31m"
#define COLOR_BLUE "\e[0;34m"
#define COLOR_WHITE "\e[1;37m"
#define COLOR_RESET "\e[0m"
#define COLOR_GREEN "\e[1;32m"

const char* questions[] = {
    "What are operations used to interact with the OS kernel called?",
    "Which kernel security feature restricts system calls?",
    "What instruction set are seccomp filters written in?",
    "Which tool can be used to read seccomp rules?",
    "When the libc open() function is called, which syscall is triggered?"
};

const char* answers[] = {
    "Syscalls",
    "Seccomp",
    "BPF",
    "seccomp-tools",
    "openat"
};

void banner() {
    puts(COLOR_RED"\t______________________  _________\n"
         "\t___  __ )__  ____/_  / / /_  ___/\n"
         COLOR_BLUE"\t__  __  |_  __/  _  / / /_____ \\ \n"
         "\t_  /_/ /_  /___  / /_/ / ____/ / \n"
         COLOR_WHITE"\t/_____/ /_____/  \\____/  /____/  \n"
         "                                     LEVEL 3\n"
        COLOR_RED"Binary"COLOR_BLUE" Exploitation Unit"COLOR_WHITE" of Serbia\n"COLOR_RESET);
    puts("Answer the questions to continue to the next level");
}

bool question(int i) {
    char ans[128];
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

void setup_seccomp() {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_openat, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL)
    };
    
    struct sock_fprog prog = {
        .len = sizeof(filter) / sizeof(filter[0]),
        .filter = filter
    };
    
    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
    prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
}

int main() {
    char buf[128];
    int cnt = 0;

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    setup_seccomp();

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