#include <png.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "ec.h"

#define ERROR 1
#define NOT_PNG 2
#define UNKNOWN_ERROR -1
#define PNG_SIG_LENGTH 8

void print_usage() { printf("Usage: decode <png file>\n"); }

int main(int argc, char** argv) {
  if (argc != 2) {
    print_usage();
    return (ERROR);
  }

  char* input_png_filename = argv[1];

  FILE* input_png_fp = fopen(input_png_filename, "rb");
  if (!input_png_fp) {
    print_usage();
    return (ERROR);
  }

  unsigned char header[PNG_SIG_LENGTH];
  fread(header, 1, PNG_SIG_LENGTH, input_png_fp);
  if (png_sig_cmp(header, 0, PNG_SIG_LENGTH)) {
    printf("File is not a PNG\n");
    return (NOT_PNG);
  }

  png_structp readp =
      png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!readp) return UNKNOWN_ERROR;
  png_infop infop = png_create_info_struct(readp);
  if (!infop) {
    png_destroy_read_struct(&readp, NULL, NULL);
    return UNKNOWN_ERROR;
  }

  png_init_io(readp, input_png_fp);
  png_set_sig_bytes(readp, PNG_SIG_LENGTH);
  png_read_png(readp, infop, PNG_TRANSFORM_IDENTITY, NULL);
  png_bytepp rowspp = png_get_rows(readp, infop);
  fclose(input_png_fp);

  int width = png_get_image_width(readp, infop);
  int height = png_get_image_height(readp, infop);
  uint64_t secret = 0;
  png_timep timep = NULL;
  if (!png_get_tIME(readp, infop, &timep) || !timep) {
    fprintf(stderr, "Missing PNG tIME chunk for EC seed.\n");
    return (UNKNOWN_ERROR);
  }

  struct tm tm_utc;
  memset(&tm_utc, 0, sizeof(tm_utc));
  tm_utc.tm_year = timep->year - 1900;
  tm_utc.tm_mon = timep->month - 1;
  tm_utc.tm_mday = timep->day;
  tm_utc.tm_hour = timep->hour;
  tm_utc.tm_min = timep->minute;
  tm_utc.tm_sec = timep->second;

  time_t secret_time = timegm(&tm_utc);
  if (secret_time == (time_t)-1) {
    fprintf(stderr, "Failed to convert PNG time to epoch.\n");
    return (UNKNOWN_ERROR);
  }
  secret = (uint64_t)secret_time;

  ECPoint G = ec_generator();
  ECPoint point = ec_mul(G, secret);

  printf("Message: ");
  while (1) {
    char buffer = 0;
    for (int b = 0; b < 7; b++) {
      uint64_t pixel_idx = point.x % ((uint64_t)width * height);
      int x = (int)(pixel_idx % width);
      int y = (int)(pixel_idx / width);

      buffer |= ((*(rowspp[y] + x) & 1) << b);
      point = ec_add(point, G);
    }
    if (!buffer) break;
    putc(buffer, stdout);
  }
  puts("\nFinished.\n");
  return 0;
}
