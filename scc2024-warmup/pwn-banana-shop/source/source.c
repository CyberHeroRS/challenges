#include <stdio.h>

int main()
{
    int money = 1000, choice, amount, active = 1;
    puts("🍌 Welcome to Banana Shop! 🍌");
    puts("If you have enough money you can buy something other than bananas.");
    while (active)
    {
        printf("\nYou have %d din! 💵\n\n", money);
        puts("1 - Buy Bananas (1kg = 50 din) 🍌");
        puts("2 - Buy Flag (13620000 din) 🚩");
        puts("3 - Exit 🚪");
        printf("Choose action > ");
        fflush(stdout);
        scanf("%d", &choice);

        switch (choice)
        {
        case 1:
            printf("Enter amount of bananas you want to buy (kg): ");
            fflush(stdout);
            scanf("%d", &amount);
            if (amount * 50 > money)
            {
                puts("You don't have enough money!");
                break;
            }
            money -= amount * 50;
            printf("You bought %dkg of bananas!\n", amount);
            break;
        case 2:
            if (money < 13620000)
            {
                puts("You don't have enough money!");
                break;
            }
            money -= 13620000;
            puts("Flag is: SCC{b4n4n45_4r3_50m371m35_b3773r_7h4n_fl465!}");
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