#include <stdio.h>
#include <stdlib.h>

int main() {
  srand(0);
  for (int i = 0; i < 30; i++) {
    int curr = (rand() % 800) & 0xFF;
    printf("%d,", curr);
  }
}