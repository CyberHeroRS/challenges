#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>

#define N 6
#define BLOCK_SIZE 256

typedef unsigned char type;
type *gflog;
type *gfilog;
type* disks[N + 2];

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
	FILE *files[N + 2];

    for (int i = 0; i < N + 2; i++) {
        disks[i] = (type*)malloc(sizeof(type) * BLOCK_SIZE);

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
        files[i] = fopen(filename, "rb");

        if (files[i] == NULL) {
            continue;
        }

        size_t bytesRead = fread(disks[i], 1, BLOCK_SIZE, files[i]);
        if (bytesRead < BLOCK_SIZE) {
            perror("Error reading to file");
        	exit(EXIT_FAILURE);
		}

		fclose(files[i]);
    }
}

void read_from_disks()
{
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

void write_to_disk()
{
    FILE* output = fopen("output.txt", "wb");
    for (int i = 0; i < N; i++) {
        size_t bytesWritten = fwrite(disks[i], 1, BLOCK_SIZE, output);
        if (bytesWritten < BLOCK_SIZE) {
            perror("Error writing to file");
        	exit(EXIT_FAILURE);
		}

    }
	fclose(output);
}

void restore_disks() {
    int d1 = 4;
    int d2 = 5;
    for (int i = 0; i < BLOCK_SIZE; i++) {
        unsigned int p = disks[N][i];
        unsigned int q = disks[N + 1][i];
        
        for (int j = 0; j < N; j++) {
            if (j == d1 || j == d2) {
                continue;
            }
            p ^= disks[j][i];
            q ^= gfilog[(j + gflog[disks[j][i]]) % 255];
        }
        
        unsigned int f, s;
        for (f = 0; f < 256; f++) {
            for (s = 0; s < 256; s++) {
                if ((f ^ s) == p && (gfilog[(d1 + gflog[f]) % 255] ^ gfilog[(d2 + gflog[s]) % 255]) == q) {
                    disks[d1][i] = f;
                    disks[d2][i] = s;
                }
            }
        }
    }
}

int main()
{
    gen_tables(8);
	init_disks();
	read_from_disks();
    restore_disks();
    write_to_disk();
}