#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

struct card_info_t {
    char number[20];
    char pin[5];
    uint64_t balance; 
};

int main() {
    int active = 1, choice, amount;
    struct card_info_t card_info;

    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    card_info.balance = 1000;
    strcpy(card_info.number, "4400 5678 9012 3456");
    puts("🍉 Welcome to Watermelon Shop! 🍉");
    puts("If you have enough money on your card you can buy something other than watermelons.");
    while (1) {
        printf("\nYou have %llu din on your card %s! 💳\n\n", card_info.balance, card_info.number);
        puts("1 - Buy Watermelons (1kg = 50 din) 🍉");
        puts("2 - Buy Flag (13620000 din) 🚩");
        puts("3 - Exit 🚪");
        printf("Choose action > ");
        scanf("%d", &choice);

        switch (choice)
        {
        case 1:
            printf("Enter amount of watermelons you want to buy (kg): ");
            scanf("%d", &amount);
            printf("Enter your PIN: ");
            scanf("%s", card_info.pin);
            if (strcmp(card_info.pin, "4267")) {
                puts("Wrong PIN!");
                break;
            }
            if (amount > card_info.balance / 50)
            {
                puts("You don't have enough money!");
                break;
            }
            card_info.balance -= amount * 50;
            printf("You bought %dkg of watermelons!\n", amount);
            break;
        case 2:
            printf("Enter your PIN: ");
            scanf("%s", card_info.pin);
            if (strcmp(card_info.pin, "4267")) {
                puts("Wrong PIN!");
                break;
            }
            if (card_info.balance < 13620000)
            {
                puts("You don't have enough money!");
                break;
            }
            card_info.balance -= 13620000;
            printf("Flag is: %s", getenv("FLAG"));
            break;
        case 3:
            active = 0;
            break;
        default:
            puts("Invalid choice!");
            break;
        }
    }
    return 0;
}