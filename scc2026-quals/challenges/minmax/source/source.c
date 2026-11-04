#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

#define BUF_SIZE 1024

FILE* secret;

void init() {
    setbuf(stdin, 0);
    setbuf(stdout, 0);
    setbuf(stderr, 0);
}

void admin_panel() {
    char buffer[BUF_SIZE];
    getchar();
    printf("Enter secret password: ");
    fgets(buffer, BUF_SIZE, stdin);
    buffer[strcspn(buffer, "\n")] = 0;
    if (strcmp(buffer, "h@cK3R/")) {
        puts("Wrong password!");
        return;
    }
    puts("Reading secrets...");
    fgets(buffer, BUF_SIZE, secret);
    sleep(3);
    puts("Something went wrong, aborting!");
    sleep(3);
}

void minmax(int min, int n) {
    int64_t numbers[BUF_SIZE / 8];
    uint8_t i, mi;
    if (n > BUF_SIZE / 8) {
        puts("Too many numbers!");
        return;
    }
    printf("Enter numbers: ");
    for (i = 0; i < n; i++) {
        scanf("%lld", numbers+i);
    }
    mi = 0;
    for (i = 1; i < n; i++) {
        if (min && numbers[i] < numbers[mi])
            mi = i;
        else if(!min && numbers[i] > numbers[mi])
            mi = i;
    }
    printf("%hhu. is %s number.\n", mi+1, min ? "the smallest" : "the largest");
}

int main() {
    init();
    secret = fopen("flag.txt", "r");
    int n, choice;
    char buf[4];
    while (1) {
        puts("\n======= MINMAX ADMIN COMPARATOR =======");
        puts("1 - Compare array of numbers.");
        puts("0 - Exit.");
        printf("> ");
        scanf("%d", &choice);
        if (choice == 0) {
            puts("Goodbye.");
            break;
        }
        else if (choice == 1) {
            printf("How many numbers? > ");
            scanf("%d", &n);
            printf("min/max? > ");
            scanf("%3s", buf);
            minmax(strcmp(buf, "min") == 0, n);
        }
        else if (choice == 0x1337) {
            admin_panel();
        }
        else {
            puts("Invalid operation.");
        }
    }
    fclose(secret);
    return 0;
}