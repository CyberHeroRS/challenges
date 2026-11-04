#include <png.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "ec.h"

#define ERROR 1
#define NOT_PNG 2
#define UNKNOWN_ERROR -1
#define PNG_SIG_LENGTH 8

typedef struct dimensions {
  int width;
  int height;
} dimensions;

void print_usage() {
  printf("Usage: stego <png_file> <output_file> <message>\n");
}


void encode_message(png_bytepp bytes, dimensions dim, char* message,
                    uint64_t secret) {
  int len = strlen(message);

  ECPoint G = ec_generator();
  ECPoint point = ec_mul(G, secret);

  for (int i = 0; i <= len; i++) {
    for (int b = 0; b < 7; b++) {
      uint64_t pixel_idx = point.x % ((uint64_t)dim.width * dim.height);
      int x = (int)(pixel_idx % dim.width);
      int y = (int)(pixel_idx / dim.width);

      if (((message[i] >> b) & 1) != 0) {
        *(bytes[y] + x) |= 1;
      } else {
        *(bytes[y] + x) &= 0xFE;
      }

      point = ec_add(point, G);
    }
  }
}

void write_new(char* output_png_filename, png_infop png_info,
               png_bytepp rowspp) {
  FILE* output_png_fp = fopen(output_png_filename, "wb");
  if (!output_png_fp) exit(UNKNOWN_ERROR);
  png_structp writep =
      png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  png_init_io(writep, output_png_fp);
  png_set_rows(writep, png_info, rowspp);
  png_write_png(writep, png_info, PNG_TRANSFORM_IDENTITY, NULL);
  fclose(output_png_fp);
}

int main(int argc, char** argv) {
  if (argc != 4) {
    print_usage();
    exit(ERROR);
  }

  char* input_png_filename = argv[1];
  char* output_png_filename = argv[2];
  char* message = argv[3];

  FILE* input_png_fp = fopen(input_png_filename, "rb");
  if (!input_png_fp) {
    print_usage();
    exit(ERROR);
  }

  unsigned char header[PNG_SIG_LENGTH];
  fread(header, 1, PNG_SIG_LENGTH, input_png_fp);
  if (png_sig_cmp(header, 0, PNG_SIG_LENGTH)) {
    printf("File is not a PNG\n");
    exit(NOT_PNG);
  }

  png_structp readp =
      png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!readp) return UNKNOWN_ERROR;
  png_infop infop = png_create_info_struct(readp);
  if (!infop) {
    exit(UNKNOWN_ERROR);
  }

  png_init_io(readp, input_png_fp);
  png_set_sig_bytes(readp, PNG_SIG_LENGTH);
  png_read_png(readp, infop, PNG_TRANSFORM_IDENTITY, NULL);
  png_bytepp rowspp = png_get_rows(readp, infop);
  fclose(input_png_fp);

  dimensions dim;
  dim.width = png_get_image_width(readp, infop);
  dim.height = png_get_image_height(readp, infop);

  time_t secret_time = time(NULL);
  uint64_t secret = (uint64_t)secret_time;
  encode_message(rowspp, dim, message, secret);

  struct tm* utc_time = gmtime(&secret_time);
  if (utc_time) {
    png_time png_time_value;
    png_time_value.year = utc_time->tm_year + 1900;
    png_time_value.month = utc_time->tm_mon + 1;
    png_time_value.day = utc_time->tm_mday;
    png_time_value.hour = utc_time->tm_hour;
    png_time_value.minute = utc_time->tm_min;
    png_time_value.second = utc_time->tm_sec;
    png_set_tIME(readp, infop, &png_time_value);
  }

  write_new(output_png_filename, infop, rowspp);

  return 0;
}
