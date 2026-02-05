#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <time.h>

int main() {
  FILE *f = fopen("flag.enc", "rb");
  int sz;
  fread(&sz, 2, 1, f);
  int t1;
  fread(&t1, 2, 1, f);
  unsigned char *flag = malloc(sz);
  fread(flag, sz, 1, f);
  int t2;
  fread(&t2, 2, 1, f);
  fclose(f);
  time_t t = (t2 << 16) | t1;
  srand(t);
  for (int i = 0; i < sz; i++)
    printf("%c", flag[i] ^ rand());
}