// SPDX-License-Identifier: GPL-2.0
#include <linux/types.h>
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

typedef unsigned int u32;
typedef unsigned long long u64;

struct sys_enter_ctx {
  unsigned short common_type;
  unsigned char common_flags;
  unsigned char common_preempt_count;
  int common_pid;
  long id;
  unsigned long args[6];
};

#define CALLGATE_NR 0x1337
#define MAX_STEPS 64

struct {
  __uint(type, BPF_MAP_TYPE_ARRAY);
  __uint(max_entries, 1);
  __type(key, u32);
  __type(value, u32);
} state_map SEC(".maps");

struct duplet {
  __u64 a0;
  __u64 a1;
};

struct {
  __uint(type, BPF_MAP_TYPE_ARRAY);
  __uint(max_entries, MAX_STEPS);
  __type(key, u32);
  __type(value, struct duplet);
} flag_map SEC(".maps");

struct {
  __uint(type, BPF_MAP_TYPE_ARRAY);
  __uint(max_entries, 1);
  __type(key, u32);
  __type(value, u32);
} steps_map SEC(".maps");

SEC("tracepoint/raw_syscalls/sys_enter")
int callgate(struct sys_enter_ctx *ctx) {
  if (ctx->id != CALLGATE_NR)
    return 0;

  u32 key = 0;

  u32 *step = bpf_map_lookup_elem(&state_map, &key);
  if (!step) {
    return 0;
  }

  u32 *total = bpf_map_lookup_elem(&steps_map, &key);
  if (!total || *total == 0) {
    return 0;
  }

  u32 cur_step = *step;
  if (cur_step >= *total) {
    cur_step = 0;
    bpf_map_update_elem(&state_map, &key, &cur_step, BPF_ANY);
  }
  if (cur_step >= MAX_STEPS) {
    return 0;
  }

  struct duplet *expected = bpf_map_lookup_elem(&flag_map, &cur_step);
  if (!expected) {
    return 0;
  }

  if ((u64)ctx->args[0] == expected->a0 && (u64)ctx->args[1] == expected->a1) {
    u32 next = cur_step + 1;
    bpf_map_update_elem(&state_map, &key, &next, BPF_ANY);
  } else {
    u32 zero = 0;
    bpf_map_update_elem(&state_map, &key, &zero, BPF_ANY);
  }

  return 0;
}

char LICENSE[] SEC("license") = "GPL";