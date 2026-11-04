/*
 * gcc -O2 -o solve solve.c
 * ./solve
 */
#define _GNU_SOURCE
#include <linux/bpf.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

#define CALLGATE_NR 0x1337
#define MAX_STEPS 64

static int bpf_obj_get(const char *path) {
  union bpf_attr attr = {};
  attr.pathname = (uint64_t)(unsigned long)path;
  return syscall(__NR_bpf, BPF_OBJ_GET, &attr, sizeof(attr));
}

static uint32_t map_read(int fd) {
  uint32_t key = 0, val = 0;
  union bpf_attr attr = {};
  attr.map_fd = fd;
  attr.key = (uint64_t)(unsigned long)&key;
  attr.value = (uint64_t)(unsigned long)&val;
  syscall(__NR_bpf, BPF_MAP_LOOKUP_ELEM, &attr, sizeof(attr));
  return val;
}

int main(void) {
  int sfd = bpf_obj_get("/sys/fs/bpf/callgate/state");
  int tfd = bpf_obj_get("/sys/fs/bpf/callgate/steps");
  if (sfd < 0 || tfd < 0) {
    perror("bpf obj_get");
    return 1;
  }

  uint32_t total = map_read(tfd);
  printf("[*] steps: %u\n", total);

  char flag[MAX_STEPS * 2 + 1];
  memset(flag, 0, sizeof(flag));
  uint32_t solved = 0;

  while (solved < total) {
    for (int a0 = 32; a0 <= 126; a0++) {
      for (int a1 = 32; a1 <= 126; a1++) {
        for (uint32_t k = 0; k < solved; k++) {
          syscall(CALLGATE_NR, (uint8_t)flag[k * 2], (uint8_t)flag[k * 2 + 1]);
        }
        syscall(CALLGATE_NR, a0, a1);

        if (map_read(sfd) == solved + 1) {
          flag[solved * 2] = a0;
          flag[solved * 2 + 1] = a1;
          solved++;
          printf("[+] %u/%u  ('%c','%c')\n", solved, total, a0, a1);
          goto next_step;
        }
      }
    }
    printf("[-] stuck at step %u\n", solved);
    break;
  next_step:
  }

  flag[solved * 2] = '\0';
  printf("\n[!!!] FLAG: %s\n", flag);
  return 0;
}