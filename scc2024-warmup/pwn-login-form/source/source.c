// Login form
// gcc source.c -o login_form

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define USERS_SIZE 16

struct user
{
    char name[32];
    char password[32];
    int is_admin;
};

struct user users[USERS_SIZE] = {0};

int main()
{
    struct user temp_user = {0};
    int ci = 0, i, choice, found;
    while (1)
    {
        puts("====== LOGIN FORM ======");
        puts("1 - Register");
        puts("2 - Login");
        printf(">> ");
        fflush(stdout);
        scanf("%d", &choice);
        getchar();
        if (choice == 1)
        {
            if (ci >= USERS_SIZE)
            {
                puts("There are no slots for new user!\n");
                continue;
            }
            printf("Enter your name: ");
            fflush(stdout);
            gets(users[ci].name);
            printf("Enter your password: ");
            fflush(stdout);
            gets(users[ci].password);
            ci++;
            puts("You are registered!\n");
        }
        else if (choice == 2)
        {
            printf("Enter your name: ");
            fflush(stdout);
            gets(temp_user.name);
            printf("Enter your password: ");
            fflush(stdout);
            gets(temp_user.password);
            found = 0;
            for (i = 0; i < ci; i++)
            {
                if (!strcmp(temp_user.name, users[i].name) && !strcmp(temp_user.password, users[i].password))
                {
                    found = 1;
                    if (users[i].is_admin)
                    {
                        puts("Welcome admin! Here is your shell: ");
                        system("/bin/sh");
                    }
                    else
                    {
                        puts("You are logged in, but you are not an admin!\n");
                    }
                    break;
                }
            }
            if (!found)
            {
                puts("Invalid credentials!\n");
            }
        }
    }
    return 0;
}
