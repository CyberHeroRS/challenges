#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

#define MAX_TODDLERS 50
#define BIGGEST_TODDLER 0x78

typedef struct {
    char *data;
    size_t size;
} Toddler;

Toddler toddlers[MAX_TODDLERS];

void menu() {
    puts("1. Create a toddler");
    puts("2. Look at a toddler");
    puts("3. Go get milk");
    puts("4. Exit");
    printf("fate> ");
}

void create_toddler() {
    int idx;
    for (idx = 0; idx < MAX_TODDLERS; idx++) {
        if (toddlers[idx].data == NULL) break;
    }
    if (idx == MAX_TODDLERS) {
        puts("You don't have any more stamina left.");
        return;
    }

    printf("toddler size: ");
    size_t size;
    scanf("%zu", &size);
    getchar();
    if (size > BIGGEST_TODDLER) {
        puts("too big....");
        return;
    }

    toddlers[idx].size = size;
    toddlers[idx].data = malloc(size);
    printf("name: ");
    fgets(toddlers[idx].data, size, stdin);
    puts("toddler created.");
}

void get_milk() {
    printf("index: ");
    int idx;
    scanf("%d", &idx);
    getchar();
    
    if (idx < 0 || idx >= MAX_TODDLERS || !toddlers[idx].data) {
        puts("Invalid toddler.");
        return;
    }

    free(toddlers[idx].data);
    puts("gone with the wind");
}

void view_toddler() {
    puts("They are so cute right?!");
    puts("You... forgot their name?");
    printf("index: ");
    int idx;
    scanf("%d", &idx);
    getchar();

    if (idx < 0 || idx >= MAX_TODDLERS || !toddlers[idx].data) {
        puts("Invalid toddler.");
        return;
    }

    printf("name: ");
    fwrite(toddlers[idx].data, toddlers[idx].size, 1, stdout);
}

void* win;

void win_maybe() {
    if (strcmp("i will never leave another baby again\n", win) == 0) {
        system("/bin/sh");
    } else {
        printf("Head to %p, find your inner peace.\n", win);
    }
}

int main() {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);

    win = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    while (1) {
        menu();
        int choice;
        scanf("%d", &choice);
        getchar();

        switch (choice) {
            case 1: create_toddler(); break;
            case 2: view_toddler(); break;
            case 3: get_milk(); break;
            case 777: win_maybe(); break;
            case 4: exit(0);
            default: puts("invalid choice.");
        }
    }
}

