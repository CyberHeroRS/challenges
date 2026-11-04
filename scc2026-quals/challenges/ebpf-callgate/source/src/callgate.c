#define _GNU_SOURCE
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "callgate.skel.h"
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

#define MAX_STEPS 64
#define PIN_DIR "/sys/fs/bpf/callgate"

static void die(const char *msg) {
  perror(msg);
  exit(1);
}

int main(void) {
  const char *flag_env = getenv("FLAG");
  if (!flag_env || !*flag_env) {
    fprintf(stderr, "FLAG env not set\n");
    exit(1);
  }

  char flag[256];
  strncpy(flag, flag_env, sizeof(flag) - 1);
  flag[sizeof(flag) - 1] = '\0';
  unsetenv("FLAG");

  size_t flag_len = strlen(flag);
  if (flag_len % 2 != 0) {
    fprintf(stderr, "FLAG length (%zu) must be divisible by 2\n", flag_len);
    exit(1);
  }
  uint32_t total_steps = (uint32_t)(flag_len / 2);
  if (total_steps > MAX_STEPS) {
    fprintf(stderr, "FLAG too long\n");
    exit(1);
  }

  struct callgate_bpf *skel = callgate_bpf__open();
  if (!skel)
    die("callgate_bpf__open");
  if (callgate_bpf__load(skel))
    die("callgate_bpf__load");

  struct {
    uint64_t a0;
    uint64_t a1;
  } duplet;

  int flag_fd = bpf_map__fd(skel->maps.flag_map);
  for (uint32_t i = 0; i < total_steps; i++) {
    duplet.a0 = (uint8_t)flag[i * 2];
    duplet.a1 = (uint8_t)flag[i * 2 + 1];
    if (bpf_map_update_elem(flag_fd, &i, &duplet, BPF_ANY))
      die("flag_map update");
  }

  uint32_t k0 = 0;
  if (bpf_map_update_elem(bpf_map__fd(skel->maps.steps_map), &k0, &total_steps,
                          BPF_ANY))
    die("steps_map update");

  if (callgate_bpf__attach(skel))
    die("callgate_bpf__attach");

  mkdir(PIN_DIR, 0755);
  unlink(PIN_DIR "/state");
  unlink(PIN_DIR "/steps");
  if (bpf_obj_pin(bpf_map__fd(skel->maps.state_map), PIN_DIR "/state"))
    die("pin state_map");
  if (bpf_obj_pin(bpf_map__fd(skel->maps.steps_map), PIN_DIR "/steps"))
    die("pin steps_map");

  chmod(PIN_DIR, 0755);
  chmod(PIN_DIR "/state", 0644);
  chmod(PIN_DIR "/steps", 0644);

  chown(PIN_DIR "/state", 1000, 1000);
  chown(PIN_DIR "/steps", 1000, 1000);

  fprintf(stderr, "[callgate] loaded, %u steps, maps pinned at " PIN_DIR "\n",
          total_steps);

  for (;;)
    pause();

  callgate_bpf__destroy(skel);
  return 0;
}
