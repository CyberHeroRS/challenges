#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>

struct Note
{
	long content_length;
	char title[64];
	char *content;
	ulong signature;
};

typedef struct Note Note;
Note *notes[16];

Note* note_add()
{
	Note *note = (Note *)malloc(sizeof(Note));
	
	printf("Enter note title: ");
	fgets(note->title, sizeof(note->title), stdin);

	printf("Enter note content length: ");
	scanf(" %ld", &note->content_length);
	getchar();
	note->content = (char *)malloc(note->content_length);

	printf("Enter note content: ");
	fgets(note->content, note->content_length, stdin);

	return note;
}

void note_print(Note *note)
{
	printf("Title: %s", note->title);
	printf("Content: %s", note->content);
	if (note->signature != 0)
	{
		printf("Signature: %lu\n", note->signature);
	}
	else
	{
		printf("Note not signed.\n");
	}
}

void note_edit(Note *note)
{
	printf("Enter note title: ");
	fgets(note->title, sizeof(note->title), stdin);

	printf("Enter note content: ");
	fgets(note->content, note->content_length, stdin);
}

void note_sign(Note *note)
{
	if (note->signature != 0)
	{
		printf("Note already signed.\n");
		return;
	}

	note->signature = (ulong)time(NULL);
}

void note_delete(Note *note)
{
	if (note->signature != 0)
	{
		printf("Note is signed. Cannot delete.\n");
		return;
	}

	free(note->content);
	free(note);

	note = NULL;
}

void note_menu()
{
	printf("1. Add Note\n");
	printf("2. Print Note\n");
	printf("3. Edit Note\n");
	printf("4. Sign Note\n");
	printf("5. Delete Note\n");
	printf("6. Exit\n");
	printf("> ");
}

int main()
{
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);

	puts("Welcome to the Note Manager!");
	while (true) {
		note_menu();
		
		int choice;
		while (true) {
			int res = scanf(" %d", &choice);
			getchar();
			if (res == 1)
				break;
		}

		if (choice == 1)
		{
			for (int i = 0; i < 16; i++)
			{
				if (notes[i] == NULL)
				{
					notes[i] = note_add();
					break;
				}
			}
		}
		else if (choice == 2)
		{
			int index;
			printf("Enter note index to print: ");
			scanf(" %d", &index);
			getchar();
			if (index >= 0 && index < 16 && notes[index] != NULL)
			{
				note_print(notes[index]);
			}
			else
			{
				printf("Invalid note index.\n");
			}
		}
		else if (choice == 3)
		{
			int index;
			printf("Enter note index to edit: ");
			scanf(" %d", &index);
			getchar();
			if (index >= 0 && index < 16 && notes[index] != NULL)
			{
				note_edit(notes[index]);
			}
			else
			{
				printf("Invalid note index.\n");
			}
		}
		else if (choice == 4)
		{
			int index;
			printf("Enter note index to sign: ");
			scanf(" %d", &index);
			getchar();
			if (index >= 0 && index < 16 && notes[index] != NULL)
			{
				note_sign(notes[index]);
			}
			else
			{
				printf("Invalid note index.\n");
			}
		}
		else if (choice == 5)
		{
			int index;
			printf("Enter note index to delete: ");
			scanf(" %d", &index);
			getchar();
			if (index >= 0 && index < 16 && notes[index] != NULL)
			{
				note_delete(notes[index]);
				printf("Note deleted.\n");
			}
			else
			{
				printf("Invalid note index.\n");
			}
		}
		else if (choice == 6)
		{
			break;
		}
		else
		{
			printf("Invalid choice. Please try again.\n");
		}
	}
}
