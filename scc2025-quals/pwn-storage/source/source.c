#include <stdio.h>
#include <stdlib.h>

char* storage[16];
int size;
int reads_left = 1;

int main() {
    int choice;
    unsigned int msize;
    char* s;
    char* ps;
    FILE* fp;

    setbuf(stdout, 0);
    setbuf(stdin, 0);

    while(1) {
        puts("\nWelcome to Storage, place where you can store any text you want!");
        puts("1 - Store text");
        puts("2 - Delete text");
        puts("3 - Read text");
        puts("4 - Exit");
        printf("Choose option > ");
        scanf("%d", &choice);

        switch(choice) {
            case 1:
                if(size == 16) {
                    puts("Storage is full!");
                }
                else {
                    printf("Enter size of text: ");
                    scanf("%u", &msize);
                    if(msize <= 0x1000) {
                        s = malloc(msize);
                        printf("Enter text content: ");
                        getchar();
                        fgets(s, msize, stdin);
                        storage[size++] = s;
                        puts("New text is stored!\n");
                    } else {
                        puts("Size of text is too big!\n");
                    }
                }
                break;
            case 2:
                if(size) {
                    free(storage[--size]);
                    storage[size] = NULL;
                    puts("Last text is deleted!");
                } else {
                    puts("Storage is empty!");
                }
                break;
            case 3:
                if(reads_left) {
                    printf("Enter index of text: ");
                    scanf("%u", &msize);
                    if(msize < size) {
                        --reads_left;
                        s = storage[msize];
                        printf("Content of chosen text: ");
                        printf(s);
                    } else {
                        puts("Invalid index!");
                    }
                } else {
                    puts("You can't read text anymore!");
                }
                break;
            case 4:
                exit(0);
            case 0x1337:
                fp = fopen("flag", "r");
                ps = malloc(0x40);
                fgets(ps, 0x40, fp);
                fclose(fp);
                ps = (char*)&s;
                break;
            default:
                puts("Invalid option!");
                break;
        }
    }
}