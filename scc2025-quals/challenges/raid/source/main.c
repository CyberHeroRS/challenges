// gcc -O3 main.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>

#define N 6
#define BLOCK_SIZE 256

char* disks[N + 2];

typedef unsigned char type;
type *gflog;
type *gfilog;

void gen_tables(int s)
{
	unsigned int b, index, gf_elements;
	unsigned int prim_poly_8 = (1 << 8) + (1 << 4) + (1 << 3) + (1 << 2) + (1 << 0);
	gf_elements = 1 << s;
	gflog = (type*)malloc(sizeof(type) * gf_elements);
	gfilog = (type*)malloc(sizeof(type) * gf_elements);
	b = 1;
	for (index = 0; index < gf_elements - 1; index++) {
		gflog[b] = (type)index;
		gfilog[index] = (type)b;
		b <<= 1;
		if (b & gf_elements)
			b ^= prim_poly_8;
	}
}

void init_disks()
{
	// has to be larger than N * BLOCK_SIZE bytes
	FILE* f = fopen("./input.txt", "r");
	if (f == NULL) {
		perror("Error input.txt not existing\n");
        exit(EXIT_FAILURE);
	}

	for (int i = 0; i < N + 2; i++) {
		disks[i] = (char*)malloc(sizeof(char) * BLOCK_SIZE);
    	size_t bytesRead = fread(disks[i], 1, BLOCK_SIZE, f);
	}
	
	fclose(f);
}

void gen_p()
{
	for (int i = 0; i < BLOCK_SIZE; i++) {
		type x = disks[0][i];
		for (int j = 1; j < N; j++) {
			x ^= disks[j][i];
		}
		disks[N][i] = x;
	}
}

void gen_q()
{
	for (int i = 0; i < BLOCK_SIZE; i++) {
		type x = disks[0][i];
		for (int j = 1; j < N; j++) {
			x ^= gfilog[(j + gflog[disks[j][i]]) % 255];
		}
		disks[N + 1][i] = x;
	}
}

void write_to_disks()
{
    const char *dir_name = "disks";
    mkdir(dir_name);

	FILE *files[N + 2];

    for (int i = 0; i < N + 2; i++) {
		char c;
		if (i == N) {
			c = 'p';
		} else if (i == N + 1) {
			c = 'q';
		} else {
			c = '0' + i;
		}

        char filename[20];
        snprintf(filename, sizeof(filename), "disks/disk_%c\0", c);
        files[i] = fopen(filename, "wb");

        if (files[i] == NULL) {
            perror("Error opening disks for writing");
        	exit(EXIT_FAILURE);
        }

        size_t bytesWritten = fwrite(disks[i], 1, BLOCK_SIZE, files[i]);
        if (bytesWritten < BLOCK_SIZE) {
            perror("Error writing to file");
        	exit(EXIT_FAILURE);
		}

		fclose(files[i]);
    }
}

int main()
{
    gen_tables(8);
	init_disks();
	gen_p();
	gen_q();
	write_to_disks();
}