#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#define MAX_MSG_SIZE 0x100

void rot(char* lv, int amount) {
  uint32_t length = ((uint32_t*)lv)[0];
  char* value = lv + 4;

  char* result = calloc(1, length);
  for (int i = 0; i < length; ++i) {
    if (value[i] >= 'a' && value[i] <= 'z') {
      result[i] = ((value[i] - 'a' + amount) % 26) + 'a';
    } else if (value[i] >= 'A' && value[i] <= 'Z'){
      result[i] = ((value[i] - 'A' + amount) % 26) + 'A';
    }
  }

  puts("Encrypted message:");
  write(1, result, length);
}

void rot13(char* lv) {
  rot(lv, 13);
}

void rot26(char* lv) {
  rot(lv, 26);
}

void rot_the_flag() {
  int fd = open("./flag.txt", O_RDONLY);
  if (fd < 0) {
    perror("open");
    exit(1);
  }

  char flag[0x100] = {};
  read(fd, flag, 0x100);

  char buf[0x104] = {};
  ((uint32_t*)buf)[0] = 0x100;
  memcpy(buf + 4, flag, 0x100);
  
  puts("lets all love aarch64");
  rot13(buf);
}

void append_msg(char* buf, char* buf2, uint32_t len) {
  for (int i = 0; i < len; ++i) {
    buf[i + MAX_MSG_SIZE] = buf2[i];
  }
}

static const char base64_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                   "abcdefghijklmnopqrstuvwxyz"
                                   "0123456789+/";

static const char base64_pad = '=';

static int base64_char_index(char c) {
  if (c >= 'A' && c <= 'Z')
    return c - 'A';
  if (c >= 'a' && c <= 'z')
    return c - 'a' + 26;
  if (c >= '0' && c <= '9')
    return c - '0' + 52;
  if (c == '+')
    return 62;
  if (c == '/')
    return 63;
  return -1;
}

void base64(char* lv) {
  char buf[MAX_MSG_SIZE] = {};
  char buf2[MAX_MSG_SIZE] = {};
  uint32_t length = ((uint32_t*)lv)[0];
  int ret = 0;
  size_t output_length, i = 0, j = 0;
  char* encoded_data = NULL;

  if (length > MAX_MSG_SIZE) {
    puts("input the rest of the message");

    ret = read(0, buf2, length - MAX_MSG_SIZE);
    if (ret < 0) {
      perror("read");
      exit(1);
    }

    append_msg(buf, buf2, ret);
  }

  output_length = 4 * ((length + 2) / 3);
  encoded_data = malloc(output_length + 1);
  
  while (i < MAX_MSG_SIZE ) {
      unsigned char byte1 = i < MAX_MSG_SIZE ? buf[i++] : 0;
      unsigned char byte2 = i < MAX_MSG_SIZE ? buf[i++] : 0;
      unsigned char byte3 = i < MAX_MSG_SIZE ? buf[i++] : 0;
      
      unsigned int triple = (byte1 << 16) | (byte2 << 8) | byte3;
      
      encoded_data[j++] = base64_chars[(triple >> 18) & 0x3F];
      encoded_data[j++] = base64_chars[(triple >> 12) & 0x3F];
      encoded_data[j++] = base64_chars[(triple >> 6) & 0x3F];
      encoded_data[j++] = base64_chars[triple & 0x3F];
  }
  
  encoded_data[output_length] = '\0';
  puts("Encrypted message:");
  write(1, encoded_data, output_length);
}

void parse_message(char* message) {
  uint32_t t = ((uint32_t*)message)[0];
  switch (t) {
  case 'R':
    rot13(message + 4);
    break;
  case 'B':
    base64(message + 4);
    break;
  case '6':
    rot26(message + 4);
    break;
  default:
    puts("Bad T in your TLV!");
    exit(1);
  }
}

int main() {
  setbuf(stdout, NULL);
  setbuf(stdin, NULL);

  puts("After seeing https://gpg.fail/ I decided that 40 year old cryptography "
       "cannot be trusted.");
  puts("To solve that, I am rolling my own, impossible-to-break cryptosystem!");
  printf("Your message in my super secure message format: ");

  char buf[MAX_MSG_SIZE] = {};
  int ret = read(0, buf, MAX_MSG_SIZE);

  if (ret < 0) {
    perror("read");
    return 1;
  }

  if (ret < 5) {
    puts("too short. don't you know the format?");
    return 1;
  }

  parse_message(buf);

  return 0;
}
