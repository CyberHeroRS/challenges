#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void setup()
{
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

void tool_echo()
{
	char buf[280];
	int size;

	printf("Echo length:");
	scanf("%hhu", &size);
	getchar();

	printf("Echo content:");
	fgets(buf, size, stdin);

	puts(buf);
}

void tool_calc()
{
	int a, b;
	char op;
	printf("Input:");
	scanf("%d %c %d", &a, &op, &b);

	switch (op)
	{
		case '+':
			printf("%d\n", a + b);
			break;
		case '-':
			printf("%d\n", a - b);
			break;
		case '*':
			printf("%d\n", a * b);
			break;
		case '/':
			printf("%d\n", a / b);
			break;
		default:
			puts("Invalid operator");
	}
}

void tool_guess()
{
	int num, guess;
	
	srand(time(NULL));
	num = rand() % 100;

	while (1)
	{
		printf("Guess the number:");
		scanf("%d", &guess);

		if (guess < num)
			puts("Too small!");
		else if (guess > num)
			puts("Too big!");
		else
		{
			puts("Correct!");
			break;
		}
	}
}

void tool_stats()
{
	int n, sum = 0;
	printf("Number of elements:");
	scanf("%d", &n);
	if (n <= 0 || n > 1000)
	{
		puts("Invalid number of elements");
		return;
	}

	int arr[n];
	printf("Elements:");
	for (int i = 0; i < n; i++)
	{
		scanf("%d", &arr[i]);
		sum += arr[i];
	}

	printf("Sum: %d\n", sum);
	printf("Average: %.2f\n", (double)sum / n);
}

void menu()
{
	printf("1. Echo\n");
	printf("2. Calculator\n");
	printf("3. Guess the number\n");
	printf("4. Statistics\n");
	printf("5. Exit\n");
	printf("> ");
}

int main()
{
	setup();

	printf("I've been learning C for a week now and I want to share some tools I've made! Have fun :)\n");

	while (1)
	{
		menu();
		int choice;
		scanf("%d", &choice);
		getchar();

		switch (choice)
		{
			case 1:
				tool_echo();
				break;
			case 2:
				tool_calc();
				break;
			case 3:
				tool_guess();
				break;
			case 4:
				tool_stats();
				break;
			case 5:
				puts("Goodbye!");
				return 0;
			default:
				puts("Invalid choice");
		}
	}

	return 0;
}
