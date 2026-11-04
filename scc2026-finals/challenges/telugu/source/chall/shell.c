#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "structs.c"
#include "cmds.c"

Dir *cwd;

void setup()
{
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
};

int main()
{
	setup();

	Dir *root = (Dir*)malloc(sizeof(Dir));
	strcpy(root->name, "/");
	root->parent = NULL;
	root->child_count = 0;
	root->file_count = 0;
	cwd = root;

	char command[256];
	while (1)
	{
		printf("shell> ");
		if (fgets(command, sizeof(command), stdin) == NULL)
			break;

		size_t len = strlen(command);
		if (len > 0 && command[len - 1] == '\n')
			command[len - 1] = '\0';

		if (strncmp(command, "exit", 4) == 0)
			break;
		else if (strncmp(command, "help", 4) == 0)
			cmd_help();
		else if (strncmp(command, "echo", 4) == 0)
			cmd_echo(command + 5);
		else if (strncmp(command, "ls", 2) == 0)
			cmd_ls();
		else if (strncmp(command, "cd", 2) == 0)
			cmd_cd(command + 3);
		else if (strncmp(command, "cat", 3) == 0)
			cmd_cat(command + 4);
		else if (strncmp(command, "mkdir", 5) == 0)
			cmd_mkdir(command + 6);
		else if (strncmp(command, "rmdir", 5) == 0)
			cmd_rmdir(command + 6);
		else if (strncmp(command, "rndir", 5) == 0)
			cmd_rndir(command + 6);
		else if (strncmp(command, "write", 5) == 0)
			cmd_write(command + 6);
		else if (strncmp(command, "rm", 2) == 0)
			cmd_rm(command + 3);
		else
			printf("Unknown command: %s\n", command);
	}
}
