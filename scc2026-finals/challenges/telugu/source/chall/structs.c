#ifndef STRUCTS_H
#define STRUCTS_H

struct Dir {
	char name[32];
	struct Dir *parent;

	struct Dir *children[10];
	struct File *files[10];

	int child_count;
	int file_count;
};

struct File {
	char name[32];
	struct Dir *parent;
	char content[256];
};

typedef struct Dir Dir;
typedef struct File File;

#endif
