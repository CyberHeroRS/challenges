#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "structs.c"
#include "helpers.c"

extern Dir *cwd;

void cmd_help()
{
	printf("Available commands:\n");
	printf("  help - Show this help message\n");
	printf("  echo [text] - Print the text to the console\n");
	printf("  ls - List the contents of the current directory\n");
	printf("  cd [dir] - Change the current directory\n");
	printf("  cat [file] - Display the contents of a file\n");
	printf("  mkdir [dir] - Create a new directory\n");
	printf("  rmdir [dir] - Remove an empty directory\n");
	printf("  write [file] - Create a new file with content\n");
	printf("  rm [file] - Remove a file\n");
}

void cmd_echo(const char *text)
{
	printf("%s\n", text);
}

void cmd_ls()
{
	for (int i = 0; i < cwd->child_count; i++)
		printf("%s/\n", cwd->children[i]->name);
	for (int i = 0; i < cwd->file_count; i++)
		printf("%s\n", cwd->files[i]->name);
}

void cmd_cd(const char *dir)
{
	Dir *tmp = helper_getdir((char*)dir);
	if (tmp != NULL)
	{
		cwd = tmp;
		return;
	}

	printf("Directory not found: %s\n", dir);
}

void cmd_cat(const char *filename)
{
	for (int i = 0; i < cwd->file_count; i++)
	{
		if (strcmp(cwd->files[i]->name, filename) == 0)
		{
			printf("%s", cwd->files[i]->content);
			return;
		}
	}

	printf("File not found: %s\n", filename);
}

void cmd_mkdir(const char *dir)
{
	if (cwd->child_count >= 10)
	{
		printf("Directory limit reached\n");
		return;
	}

	for (int i = 0; i < cwd->child_count; i++)
	{
		if (strcmp(cwd->children[i]->name, dir) == 0)
		{
			printf("Directory already exists: %s\n", cwd->name);
			return;
		}
	}

	Dir *new_dir = (Dir*)malloc(sizeof(Dir));
	strcpy(new_dir->name, dir);
	new_dir->parent = cwd;
	new_dir->child_count = 0;
	new_dir->file_count = 0;

	cwd->children[cwd->child_count++] = new_dir;
}

void cmd_rmdir(const char *dir)
{
	Dir *tmp = helper_getdir((char*)dir);
	if (tmp == NULL)
	{
		printf("Directory not found: %s\n", tmp->name);
		return;
	}

	if (tmp->child_count > 0 || tmp->file_count > 0)
	{
		printf("Directory not empty: %s\n", tmp->name);
		return;
	}

	int i = 0;
	while (i < cwd->child_count && tmp->parent->children[i] != tmp)
		i++;
	for (; i < cwd->child_count - 1; i++)
		cwd->children[i] = cwd->children[i + 1];

	cwd->child_count--;
	free(tmp);
}

void cmd_rndir(const char *dir)
{
	Dir *tmp = helper_getdir((char*)dir);
	if (tmp == NULL)
	{
		printf("Directory not found: %s\n", tmp->name);
		return;
	}
	if (tmp->parent == NULL)
	{
		printf("Cannot rename root directory\n");
		return;
	}

	printf("Write new name for directory: ");
	char new_name[32];
	fgets(new_name, sizeof(new_name), stdin);
	size_t len = strlen(new_name);
	if (len > 0 && new_name[len - 1] == '\n')
		new_name[len - 1] = '\0';

	for (int i = 0; i < tmp->parent->child_count; i++)
	{
		if (strcmp(tmp->parent->children[i]->name, new_name) == 0)
		{
			printf("Directory already exists: %s\n", new_name);
			return;
		}
	}

	strcpy(tmp->name, new_name);
}

void cmd_write(const char *args)
{
	if (cwd->file_count >= 10)
	{
		printf("File limit reached\n");
		return;
	}

	char filename[32];
	strncpy(filename, args, 31);
	filename[31] = '\0';

	for (int i = 0; i < cwd->file_count; i++)
	{
		if (strcmp(cwd->files[i]->name, filename) == 0)
		{
			printf("File already exists: %s\n", filename);
			return;
		}
	}

	File *new_file = (File*)malloc(sizeof(File));
	strcpy(new_file->name, filename);
	new_file->parent = cwd;
	printf("Enter file content (max 255 characters): ");
	fgets(new_file->content, sizeof(new_file->content), stdin);

	cwd->files[cwd->file_count++] = new_file;
}

void cmd_rm(const char *filename)
{
	for (int i = 0; i < cwd->file_count; i++)
	{
		if (strcmp(cwd->files[i]->name, filename) == 0)
		{
			int j = i;
			while (j < cwd->file_count - 1)
				cwd->files[j] = cwd->files[j + 1];
			cwd->file_count--;
			free(cwd->files[cwd->file_count]);
			return;
		}
	}

	printf("File not found: %s\n", filename);
}
