#include <stdio.h>
#include <string.h>
#define FLAG_LENGTH "flag_length"

const unsigned char ENC_FLAG[] = "flag";
const unsigned char KEY[] = "key";

unsigned char transform_byte(unsigned char b, unsigned char k, unsigned int i) {
  unsigned char v = (unsigned char)((b ^ k) + 0x35u - (unsigned char)(i * 5u));
  v = (unsigned char)((unsigned char)(v << 1) | (unsigned char)(v >> 7));
  v ^= 0xA7u;
  return v;
}

int check_flag(const unsigned char* inp, unsigned int n) {
  unsigned int i;

  if (n != FLAG_LENGTH) {
    return 0;
  }

  for (i = 0; i < FLAG_LENGTH; i++) {
    if (transform_byte(inp[i], KEY[i], i) != ENC_FLAG[i]) {
      return 0;
    }
  }

  return 1;
}

int main(void) {
  unsigned char input[FLAG_LENGTH + 1];
  size_t len;

  printf("What is the flag?\n> ");

  if (!fgets((char*)input, FLAG_LENGTH + 1, stdin)) {
    printf("Input error\n");
    return 1;
  }
  puts("");

  len = strlen((char*)input);
  if (len > 0 && input[len - 1] == '\n') {
    input[len - 1] = '\0';
    len--;
  }

  if ((unsigned int)len != FLAG_LENGTH) {
    printf("Try again\n");
    return 1;
  }

  if (!check_flag(input, (unsigned int)len)) {
    printf("Try again\n");
    return 1;
  }

  printf("Correct!\n");
  return 0;
}
