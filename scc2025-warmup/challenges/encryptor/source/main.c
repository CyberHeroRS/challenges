#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <time.h>

int main() {
  time_t t = time(0);
  srand(t);
  FILE *f = fopen("flag", "rb");
  fseek(f, SEEK_SET, SEEK_END);
  long size = ftell(f);
  fseek(f, SEEK_SET, SEEK_SET);
  unsigned char *data = malloc(size);
  fread(data, size, 1, f);
  fclose(f);
  f = fopen("flag.enc", "wb");
  fwrite(&size, 2, 1, f);
  fwrite(&t, 2, 1, f);
  for (int i = 0; i < size; i++)
    data[i] ^= rand();
  fwrite(data, size, 1, f);
  t >>= 16;
  fwrite(&t, 2, 1, f);
  fclose(f);
}