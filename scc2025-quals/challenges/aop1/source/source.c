#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define CLEAR "\x1b[2J\x1b[H"
#define RESET   "\x1b[0m"

#define LEGENDARY "\x1b[38;5;214m"
#define EPIC      "\x1b[38;5;93m"
#define RARE      "\x1b[38;5;33m"
#define COMMON    "\x1b[38;5;8m"

#define BOLD_LEGENDARY "\x1b[1;38;5;214m"
#define BOLD_RARE      "\x1b[1;38;5;33m"
#define FOREST_GREEN   "\x1b[38;5;28m"
#define BOLD_WHITE     "\x1b[1;37m"
#define BOLD_RED       "\x1b[1;31m"
#define BOLD_GREEN     "\x1b[1;32m"
#define BOLD_BLUE      "\x1b[1;34m"
#define BOLD_YELLOW    "\x1b[1;33m"

#define WEAPON_COUNT 13

typedef struct {
    const char* name;
    int level;
    int strength;
    bool own;
} weapon_t;

typedef struct {
    const char* name;
    int level;
    int damage;
    int health;
} enemy_t;

typedef struct {
    int level;
    int exp;
    int weapon;
    int health;
    int potions;
    int gold;
} player_t;

weapon_t weapons[] = {
    { "Bare Hands", 1, 6, true },
    { "Byte Dagger", 1, 10, false },
    { "Phishing Hook", 1, 12, false },
    { "Packet Spear", 1, 8, false },
    { "Malware Mace", 2, 20, false },
    { "Cipher Crossbow", 2, 15, false },
    { "Firewall Flail", 2, 18, false },
    { "Zero-Day Blade", 3, 25, false },
    { "Wormwood Staff", 3, 30, false },
    { "Backdoor Bow", 3, 22, false },
    { "Rootkit Scythe", 4, 35, false },
    { "Quantum Sabre", 4, 40, false },
    { "Kernel Sword", 4, 45, false }
};
const char* weapon_ranks[] = {"Common", "Rare", "Epic", "Legendary"};
const char* weapon_colors[] = {COMMON, RARE, EPIC, LEGENDARY};

enemy_t enemies[] = {
    { "Stack Goblin", 1, 5, 20 },
    { "Buffer Gremlin", 1, 6, 18 },
    { "Stack Wolf", 2, 10, 40 },
    { "Segtroll", 2, 12, 46 },
    { "BoF Ghoul", 3, 18, 65 },
    { "Segfault Serpents", 3, 15, 60 }
};

enemy_t boss = { "Binary Hydra", 4, 50, 1000 };
bool is_boss_defeated = false;
bool has_key = false;
player_t player = { 1, 0, 0, 20, 0, 10 };

int min(int a, int b) {
    return a < b ? a : b;
}

void game_over(const char* killer) {
    printf(CLEAR);
    puts(BOLD_WHITE"GAME OVER"RESET);
    printf("You were killed by %s%s\n\n"RESET, BOLD_RED, killer);
    exit(0);
}

void print_stats() {
    printf("%32c%sLevel: %s%d%s   Exp: %s%d%s   Gold: %s%d\n"RESET, ' ', BOLD_WHITE, BOLD_BLUE, player.level, BOLD_WHITE, BOLD_GREEN, player.exp, BOLD_WHITE, BOLD_YELLOW, player.gold);
    printf("%32c%sPotions: %s%d\n"RESET, ' ', BOLD_WHITE, BOLD_RARE, player.potions);
}

int get_int() {
    char buf[16];

    fgets(buf, 16, stdin);
    return atoi(buf);
}

void shop() {
    int i, j, price, choice, amount;

    while(true) {
        printf(CLEAR);
        puts("You enter "LEGENDARY"the Shop"RESET" and a woman behind the counter looks up.");
        puts(COMMON"Nyxara:"RESET" Ah, welcome, traveler. Name's Nyxara.");
        puts("I've got what you need for your journey—weapons,");
        puts("potions, and more. Take a look around, but don't take too long.");
        puts("Time is always running out in "FOREST_GREEN"the Stack Forest"RESET".\n");
        print_stats();
        puts(" 1. Potion - "BOLD_YELLOW"10 gold"RESET);
        i = 2;
        if(is_boss_defeated) {
            i = 3;
            puts(" 2. Treasure Key - "BOLD_YELLOW"1000000000 gold"RESET);
        }
        for(j = 0; j < WEAPON_COUNT; j++) {
            if(!weapons[j].own && weapons[j].level <= player.level) {
                price = weapons[j].level * weapons[j].level * (weapons[j].level + 4) * weapons[j].strength;
                printf(" %d. %s - %s%d gold%s - %s%s\n"RESET, i++, weapons[j].name, BOLD_YELLOW, price, RESET, weapon_colors[weapons[j].level-1], weapon_ranks[weapons[j].level-1]);
            }
        }
        printf(" %d. Leave the Shop\n\n", i);
        printf(" > ");
        choice = get_int();
        if(choice == i) {
            return;
        } else if(choice == 1) {
            printf(COMMON"Nyxara:"RESET" How many potions you need?\n");
            printf("\n > ");
            amount = get_int();
            if(amount > 0 && amount * 10 <= player.gold) {
                player.potions += amount;
                player.gold -= amount * 10;
            } else {
                puts(BOLD_WHITE"\nNot enough gold. Press Enter to continue shopping."RESET);
                getchar();
            }
            continue;
        } else if(choice <= 0 || choice > i) {
            puts(BOLD_WHITE"\nInvalid item. Press Enter to continue shopping."RESET);
            getchar();
            continue;
        }

        if(choice == 2 && is_boss_defeated) {
            if(player.gold >= 1000000000) {
                has_key = true;
                player.gold -= 1000000000;
            } else {
                puts(BOLD_WHITE"\nNot enough gold. Press Enter to continue shopping."RESET);
                getchar();
            }
            continue;
        }

        i = 2 + is_boss_defeated;
        for(j = 0; j < WEAPON_COUNT && i <= choice; j++) {
            if(!weapons[j].own && weapons[j].level <= player.level) {
                price = weapons[j].level * weapons[j].level * (weapons[j].level + 4) * weapons[j].strength;
                i++;
            }
        }
        
        if(player.gold >= price) {
            player.weapon = j-1;
            player.gold -= price;
            weapons[j-1].own = true;
        } else {
            puts(BOLD_WHITE"\nNot enough gold. Press Enter to continue shopping."RESET);
            getchar();
        }
    }
}

void switch_weapon() {
    int i, choice, j = 1;

    while(true) {
        printf(CLEAR);
        puts("You decide it's time to switch weapons.");
        puts("You browse your inventory, searching for something more suitable.\n");
        print_stats();
        
        j = 1;
        for(i = 0; i < WEAPON_COUNT; i++) {
            if(weapons[i].own)
                printf(" %2d. %s[%c]%s %s - %s%s\n"RESET, j, BOLD_GREEN, i == player.weapon ? 'U' : ' ', RESET, weapons[i].name, weapon_colors[weapons[i].level-1], weapon_ranks[weapons[i].level-1]), j++;
        }
        printf(" %2d. Stop browsing\n", j);
        printf("\n > ");
        choice = get_int();
        if(choice == j) {
            return;
        }
        if(choice <= 0 || choice > j) {
            puts(BOLD_WHITE"\nInvalid item. Press Enter to continue browsing."RESET);
            getchar();
            continue;
        }
        j = 0;
        for(i = 0; i < WEAPON_COUNT && j < choice; i++) {
            if(weapons[i].own)
                j++;
        }
        player.weapon = i-1;
    }
}

void enter_forest() {
    enemy_t enemy;
    int ei, choice;
    
    ei = rand() % (min(3, player.level) * 2);
    enemy = enemies[ei];
    while(true) {
        printf(CLEAR);
        puts("You step into the dense, shadowy woods of "FOREST_GREEN"Stack Forest."RESET);
        puts("The air is thick with the scent of damp earth and mystery.");
        puts("As you move forward, the rustling of leaves catches your attention.");
        printf("Suddenly, a %s%s%s emerges from the shadows, blocking your path.\n", BOLD_RED, enemy.name, RESET);
        puts("It growls, ready for a fight.");
        print_stats();
        printf("Your health: %s%d\n"RESET, BOLD_RED, player.health);
        printf("Enemy health: %s%d\n"RESET, BOLD_RED, enemy.health);

        puts("\n 1. Attack Enemy");
        puts(" 2. Drink Potion");
        puts(" 3. Run Away");

        printf("\n > ");
        choice = get_int();
        if(choice == 3) {
            return;
        }
        else if(choice == 2) {
            if(player.potions > 0) {
                player.health = player.level * 20;
                player.potions -= 1;
            }
            else {
                puts(BOLD_WHITE"\nYou don't have any Potion. Press Enter to return."RESET);
                getchar();
            }
        }
        else if(choice == 1) {
            enemy.health -= weapons[player.weapon].strength;
            if(enemy.health <= 0) {
                player.exp += enemy.level;
                if(player.exp >= 4 + player.level * 4) {
                    player.exp = 0;
                    player.level++;
                    player.health = player.level * 20;
                }
                player.gold += enemies[ei].health;
                if(player.gold > 10000) {
                    player.gold = 0;
                    puts(BOLD_WHITE"\nA Stack Goblin emerges from the bushes and steals all of your gold!\nPress Enter to return."RESET);
                    getchar();
                }
                ei = rand() % (min(3, player.level) * 2);
                enemy = enemies[ei];
                continue;
            }
        }
        player.health -= enemy.damage;
        if(player.health <= 0) {
            game_over(enemy.name);
        }
    }
}

void open_treasure() {
    char spell[128];
    int i;
    uint8_t power = 0;

    if(!has_key) {
        printf(CLEAR);
        puts("You approach the "BOLD_LEGENDARY"Hidden Treasure"RESET", but it remains sealed.");
        puts("The lock is sturdy, and without the key, it cannot be opened.");
        puts("The treasure lies just out of reach, waiting for you to find the missing key.");
        puts(BOLD_WHITE"\nPress Enter to return."RESET);
        getchar();
        return;
    }

    printf(CLEAR);
    puts("With the key in hand, you unlock the "BOLD_LEGENDARY"Hidden Treasure."RESET);
    puts("Inside, you find a magical scroll adorned with intricate runes.");
    puts("As you carefully unfurl the scroll, the runes begin to glow with an otherworldly light.");
    puts("Reading the runes aloud, you unlock the power within,");
    puts("preparing to cast a "EPIC"Powerful Spell"RESET" unlike any you've wielded before.\n");

    printf(" spell> ");
    fgets(spell, 128, stdin);

    for(i = 0; i < strlen(spell); i++) {
        power += spell[i];
    }
    spell[power] = spell[power / 2];
}

void fight_boss() {
    int choice;

    if(is_boss_defeated) {
        puts("You approach the area where the "BOLD_RED"Binary Hydra"RESET" once stood, but the lake's surface is calm,");
        puts("and the shadows have lifted. The beast has already been defeated. Your previous victory has cleansed the heart of "FOREST_GREEN"Stack Forest,"RESET);
        puts("and the Hydra will not return. There's nothing left to conquer here—your triumph remains.");
        puts(BOLD_WHITE"\nPress Enter to return."RESET);
        getchar();
        return;
    }

    while(true) {
        printf(CLEAR);
        puts("You step into the dense, shadowy woods of the "FOREST_GREEN"Stack Forest"RESET", with the "RARE"Lake of Null"RESET" at its heart.");
        puts("The air is thick with the scent of damp earth and mystery.");
        puts("As you move forward, the rustling of leaves catches your attention.");
        printf("Suddenly, from the depths of the lake, the %s%s%s emerges, its silhouette bathed in eerie moonlight.\n", BOLD_RED, boss.name, RESET);
        puts("It growls, ready for a fight.");
        print_stats();
        printf("Your health: %s%d\n"RESET, BOLD_RED, player.health);
        printf("Enemy health: %s%d\n"RESET, BOLD_RED, boss.health);

        puts("\n 1. Attack Enemy");
        puts(" 2. Drink Potion");

        printf("\n > ");
        choice = get_int();

        if(choice == 2) {
            if(player.potions > 0) {
                player.health = player.level * 20;
                player.potions -= 1;
            }
            else {
                puts(BOLD_WHITE"\nYou don't have any Potion. Press Enter to return."RESET);
                getchar();
            }
        }
        else if(choice == 1) {
            boss.health -= weapons[player.weapon].strength;
            if(boss.health <= 0) {
                player.exp += boss.level;
                if(player.exp >= 4 + player.level * 4) {
                    player.exp = 0;
                    player.level++;
                    player.health = player.level * 20;
                }
                player.gold += 1000;
                
                is_boss_defeated = true;
                puts("Congratulations! You've triumphed over the "BOLD_RED"Binary Hydra"RESET", proving your strength and courage.");
                puts("The "RARE"Lake of Null"RESET" now feels a little less ominous, and the shadows of "FOREST_GREEN"Stack Forest"RESET" begin to recede.");
                puts("As a reward for your bravery, you uncover a "BOLD_LEGENDARY"Hidden Treasure"RESET", waiting to be claimed. Well done, hero!");
                puts(BOLD_WHITE"\nPress Enter to return."RESET);
                getchar();
                return;
            }
        }
        player.health -= boss.damage;
        if(player.health <= 0) {
            game_over(boss.name);
        }
    }
}

void intro() {
    printf(CLEAR);
    puts(BOLD_LEGENDARY"\n\nADVENTURES OF PWNZOR I: The Stack Forest"RESET);
    puts(COMMON"Copyright (c) 2025 SCC. All rights reserved.\n\n"RESET);
    puts(LEGENDARY"Welcome to the Adventures of Pwnzor!"RESET);
    puts("In a world where technology and ancient magic collide, \n"\
    "you are a skilled cyber warrior, known only as "BOLD_RARE"Pwnzor"RESET".\n"\
    "Armed with knowledge of both the old and the new, \n"\
    "you've ventured into "FOREST_GREEN"Stack Forest"RESET",\n"\
    "a place where firewalls meet enchanted creatures, \n"\
    "and data streams flow through ancient roots.\n"\
    "This mysterious forest is filled with dangerous monsters \n"\
    "that protect dark secrets, powerful artifacts, and "EPIC"even hidden treasures."RESET"\n");
    puts(BOLD_WHITE"Press Enter to start your adventure!"RESET);
    getchar();
}

void game() {
    int choice;

    srand(time(0));
    while(true) {
        printf(CLEAR);
        puts("You are at the "BOLD_RARE"Village of Return"RESET", standing at the edge of "FOREST_GREEN"Stack Forest."RESET);
        puts("The air is thick with mystery and danger, and the path ahead is uncertain.");
        puts("Here, you may:");
        print_stats();
        puts(" 1. Visit the Shop");
        puts(" 2. Switch Weapon");
        puts(" 3. Enter Stack Forest");
        puts(" 4. Fight the Forest Boss");
        if(is_boss_defeated) puts(" 5. Open Hidden Treasure");
        printf("\n > ");
        choice = get_int();
        if(choice == 1) shop();
        else if(choice == 2) switch_weapon();
        else if(choice == 3) enter_forest();
        else if(choice == 4) fight_boss();
        else if(is_boss_defeated && choice == 5) open_treasure();
        else {
            puts(BOLD_WHITE"\nUnknown path ahead. Press Enter to return."RESET);
            getchar();
        }
    }
}

void powerful_spell() {
    printf(CLEAR);
    puts("The "EPIC"Powerful Spell"RESET" unleashes a surge of energy, and ancient text begins to materialize in the air");
    puts(", glowing with a mystical light. The words appear, written in an arcane script:");
    printf(BOLD_LEGENDARY);
    puts(getenv("FLAG"));
    printf(RESET);
    getchar();
}

int main() {
    setbuf(stdin, 0);
    setbuf(stdout, 0);
    intro();
    game();
    return 0;
}