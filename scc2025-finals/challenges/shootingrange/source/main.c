#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

char *competitors[3] = { "Alice", "Bob", "Charlie" };

// BSS
struct _competition {
	uint8_t scores[10];
} competition_you, competition_competitor;

struct _competition_scores {
	char name[8];
	uint8_t scores[16];
} competition_scores[4];

// Helpers
void get_competitor_name(char *competitor_name)
{
	printf("Enter competitor name: ");
	fgets(competitor_name, 64, stdin);
}

void print_main_menu()
{
	printf("1. Start Competition\n");
	printf("2. View Scores\n");
	printf("3. Exit\n");
	printf("> ");
}

void scores_insert(int index, uint8_t score)
{
	if (competition_scores[index].scores[15] < score)
	{
		competition_scores[index].scores[15] = score;

		for (int i = 15; i > 0; i--)
		{
			if (competition_scores[index].scores[i - 1] > competition_scores[index].scores[i])
				break;
			uint8_t temp = competition_scores[index].scores[i];
			competition_scores[index].scores[i] = competition_scores[index].scores[i - 1];
			competition_scores[index].scores[i - 1] = temp;
		}
	}
}

void scores_view(int index)
{
	printf("Scores for %s:\n", competition_scores[index].name);
	for (int i = 0; i < 10; i++)
	{
		if (competition_scores[index].scores[i] == 0)
			break;
		printf(" %d", competition_scores[index].scores[i]);
	}
	printf("\n");
}

void scores_view_choice()
{
	for (int i = 0; i < 4; i++)
		printf("%d. %s\n", i + 1, competition_scores[i].name);
	printf("Choose competitor to view scores: ");

	int choice;
	scanf("%d", &choice);
	getchar();
	
	if (choice > 3)
	{
		printf("Invalid choice.\n");
	}
	else {
		scores_view(choice - 1);
	}
}

// Competition helpers
struct _competition_result {
	int competitor_id;
	uint8_t competitor_score;
	uint8_t your_score;
};

struct _competition_shot {
	uint8_t x;
	uint8_t y;
};

void competition_menu()
{
	printf("1. Shoot\n");
	printf("2. Check score\n");
	printf("3. Exit\n");
	printf("> ");
}

struct _competition_shot competition_shoot()
{
	struct _competition_shot shot;
	shot.x = rand() % 16;
	shot.y = rand() % 16;
	return shot;
}

int competition_shot_result(struct _competition_shot shot)
{
	int x = shot.x - 8;
	int y = shot.y - 8;
	double distance = x * x + y * y;
	int offset = sqrt(distance);
	uint8_t score = 10 - offset;
	if (score < 0)
		score = 0;
	return score;
}

struct _competition_result competition_start(char* competitor_name)
{
	struct _competition_result result;
	result.competitor_id = rand() % 3;
	result.competitor_score = 0;
	result.your_score = 0;

	printf("Your competitor is %s\n", competitors[result.competitor_id]);

	for (int i = 0; i < 10; i++)
	{
		competition_you.scores[i] = 0;
		competition_competitor.scores[i] = 0;
	}

	for (int i = 0; i < 10; i++)
	{
		competition_menu();
		int choice;
		scanf("%d", &choice);
		getchar();

		switch (choice) {
			case 1:
				printf("Shooting...\n");
				struct _competition_shot shot_you = competition_shoot();
				struct _competition_shot shot_competitor = competition_shoot();
				competition_you.scores[i] = (shot_you.x << 4) | shot_you.y;
				competition_competitor.scores[i] = (shot_competitor.x << 4) | shot_competitor.y;

				int score_you = competition_shot_result(shot_you);
				int score_competitor = competition_shot_result(shot_competitor);
				result.your_score += score_you;
				result.competitor_score += score_competitor;

				printf("Your shot hit at (%d, %d) with score %d\n", shot_you.x, shot_you.y, score_you);
				printf("%s's shot hit at (%d, %d) with score %d\n", competitors[result.competitor_id], shot_competitor.x, shot_competitor.y, score_competitor);
				break;
			case 2:
				printf("Your score: %d\n", result.your_score);
				printf("%s's score: %d\n", competitors[result.competitor_id], result.competitor_score);
				break;
			case 3:
				printf("Exiting competition...\n");
				return result;
			default:
				printf("Invalid choice.\n");
		}
	}

	printf("Retake shot? (y/n): ");
	char retake;
	scanf(" %c", &retake);
	getchar();
	if (retake == 'y' || retake == 'Y')
	{
		printf("Which shot do you want to retake?\n");
		printf("> ");
		int shot_number;
		scanf("%d", &shot_number);
		getchar();

		printf("Retaking shot %d...\n", shot_number);

		if (shot_number <= 10)
		{
			struct _competition_shot shot_you = competition_shoot();
			int score = competition_shot_result(shot_you);
			printf("Your new shot hit at (%d, %d) with score %d\n", shot_you.x, shot_you.y, score);
			
			result.your_score -= competition_you.scores[shot_number - 1];
			competition_you.scores[shot_number - 1] = (shot_you.x << 4) | shot_you.y;
			result.your_score += score;
		}
	}

	return result;
}

// Main
int main()
{
	char competitor_name[32];

	srand(time(NULL));
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);

	puts("Welcome to the competition!");
	get_competitor_name(competitor_name);
	memcpy(competition_scores[3].name, competitor_name, 8);
	if (competition_scores[3].name[7] != '\0')
	{
		competition_scores[3].name[6] = '.';
		competition_scores[3].name[7] = '\0';
	}

	memcpy(competition_scores[0].name, competitors[0], 8);
	memcpy(competition_scores[1].name, competitors[1], 8);
	memcpy(competition_scores[2].name, competitors[2], 8);
	for (int i = 0; i < 4; i++)
		for (int j = 0; j < 16; j++)
			competition_scores[i].scores[j] = 0;

	while (true) {
		print_main_menu();
		int choice;
		scanf("%d", &choice);
		getchar();

		switch (choice) {
			case 1:
				printf("Starting new competition.\n");
				struct _competition_result result = competition_start(competitor_name);
				scores_insert(result.competitor_id, result.competitor_score);
				scores_insert(3, result.your_score);
				break;
			case 2:
				printf("Viewing scores.\n");
				scores_view_choice();
				break;
			case 3:
				printf("Exiting.\n");
				return 0;
			default:
				printf("Invalid choice.\n");
		}
	}

	return 0;
}
