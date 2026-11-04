#include <elf.h>
#include <linux/prctl.h>
#include <sha256.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tctildr.h>
#include <unistd.h>

#include <array>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <debugging>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

#include "generated_perm.inc"

#define SEGFAULT()                 \
  do {                             \
    state = 0xDEADBEEFDEADBEEFULL; \
    *(volatile uint64_t*)0 = 0;    \
  } while (0)

#define EXIT(status)                                                        \
  do {                                                                      \
    state = 0xDEADBEEFDEADBEEFULL;                                          \
    if (addrs[1] != ((size_t)&do_exit ^ (size_t)&anti_tamper_anchor) ||     \
        addrs[2] != ((size_t)&exit ^ (size_t)&anti_tamper_anchor) ||        \
        addrs[3] !=                                                         \
            ((size_t)&is_debugger_present ^ (size_t)&anti_tamper_anchor) || \
        addrs[4] != ((size_t)&clobber ^ (size_t)&anti_tamper_anchor)) {     \
      SEGFAULT();                                                           \
    }                                                                       \
    do_exit(status);                                                        \
  } while (0)

#define GOOD_STATE 0xDEADC0DEDEADC0DEULL
uint64_t state = GOOD_STATE;
size_t addrs[5] = {0};
void* clobber_addr = nullptr;
const uint8_t GOOD[32] = {0xb2, 0xa1, 0xf8, 0x5a, 0x6f, 0x29, 0xab, 0x0d,
                          0x99, 0x8d, 0x87, 0x71, 0x53, 0x30, 0xc4, 0x76,
                          0x66, 0x11, 0x59, 0xba, 0xcd, 0xf5, 0xbf, 0xbb,
                          0x47, 0x45, 0x57, 0xe0, 0x94, 0x6b, 0xb7, 0xc9};

static void anti_tamper_anchor() {}

extern "C" char __executable_start;
extern "C" char etext;

extern "C" void clobber_code_end();
inline __attribute__((noinline)) static void clobber_code() {
  const long page_size = sysconf(_SC_PAGESIZE);
  if (page_size <= 0) {
    return;
  }

  const auto page_mask = static_cast<uintptr_t>(page_size - 1);
  const uintptr_t text_start = reinterpret_cast<uintptr_t>(&__executable_start);
  const uintptr_t text_end = reinterpret_cast<uintptr_t>(&etext);
  const uintptr_t aligned_start = text_start & ~page_mask;
  const uintptr_t aligned_end = (text_end + page_mask) & ~page_mask;

  (void)mprotect(reinterpret_cast<void*>(aligned_start),
                 aligned_end - aligned_start,
                 PROT_READ | PROT_WRITE | PROT_EXEC);
  memset(reinterpret_cast<void*>(aligned_start), 0xCC,
         aligned_end - aligned_start);
  // We should be dead
  asm volatile(R"(
    .global clobber_code_end
    clobber_code_end:
  )");
}

inline __attribute__((always_inline, noreturn)) static void clobber() {
  // Goodbye, cruel world
  ((void (*)())clobber_addr)();
  exit(1);
  while (true) {
    asm volatile("ud2");
  }
}

void __attribute__((noinline)) __attribute__((noreturn)) do_exit(int status) {
  state = 0xDEADBEEFDEADBEEFULL;
  exit(status);
  SEGFAULT();
  // Oh no you don't
  clobber();
}

inline __attribute__((always_inline)) uint64_t rdtsc() {
  uint32_t low, high;
  asm volatile("rdtsc" : "=a"(low), "=d"(high));
  return (static_cast<uint64_t>(high) << 32) | low;
}

inline __attribute__((always_inline)) void check_cpu_capabilities() {
  uint32_t eax, ebx, ecx, edx;

  asm volatile("cpuid" : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx) : "a"(1));
  if (
      // Hypervisor check
      (ecx & (1 << 31)) != 0 &&
      // RDTSC check
      (edx & (1 << 4)) == 0 &&
      // SSE2 check
      (edx & (1 << 26)) == 0) {
    EXIT(1);
  }

  asm volatile("cpuid"
               : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
               : "a"(0x0A));
  // VMX check (some VMs might not support nested virtualisation)
  if ((eax & 0xFF) == 0) {
    EXIT(1);
  }
}

inline __attribute__((always_inline)) void timing_and_cpu_check() {
  const auto CYCLES = 10000;
  uint64_t start = rdtsc();
  for (volatile int i = 0; i < CYCLES; i += 1) {
    // empty loop to consume some time
  }
  uint64_t end = rdtsc();
  if (end <= start || end - start > (CYCLES * 6)) {
    SEGFAULT();
    EXIT(1);
  }

  char vendor[13] = {0};

  start = rdtsc();
  asm volatile(
      "mov $0, %%rax\n"
      "cpuid\n"
      "mov %%ebx, %[v1]\n"
      "mov %%edx, %[v2]\n"
      "mov %%ecx, %[v3]\n"
      : [v1] "=m"(vendor[0]), [v2] "=m"(vendor[4]), [v3] "=m"(vendor[8])
      :
      : "rax", "rbx", "rcx", "rdx");
  end = rdtsc();
  if (end <= start || end - start > 1000) {
    clobber();
    EXIT(1);
  }

  // Racism
  if (memcmp(vendor, "GenuineIntel", 12) != 0 &&
      memcmp(vendor, "AuthenticAMD", 12) != 0) {
    clobber();
    EXIT(1);
  }
}

inline __attribute__((always_inline)) int check(const char* data) {
  static_assert(sizeof(U64x4) == 32);

  array<uint64_t, 4> words{};
  memcpy(words.data(), data, sizeof(words));
  U64x4 s(words.data(), sx::element_aligned);
  timing_and_cpu_check();
  check_cpu_capabilities();
  if (is_debugger_present()) {
    s ^= make_u64x4(0xBADF00DBADF00FULL, 0xBADF00DBADF00FULL,
                    0xBADF00DBADF00FULL, 0xBADF00DBADF00FULL);
  }
  if (state != GOOD_STATE) {
    s ^= make_u64x4(state, state, state, state);
  }
  s = apply_permutation(s);
  timing_and_cpu_check();
  U64x4 expected(FLAG, sx::element_aligned);
  return sx::all_of(s == expected) ? 0 : 1;
}

inline __attribute__((always_inline)) bool is_ptraced() {
  errno = 0;
  if (ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) == -1) {
    return errno == EPERM;
  }
  ptrace(PTRACE_DETACH, 0, nullptr, nullptr);
  return false;
}

static void populate_arrs(void) __attribute__((constructor));
static void populate_arrs(void) {
  addrs[0] = reinterpret_cast<size_t>(&anti_tamper_anchor);
  addrs[1] = reinterpret_cast<size_t>(&do_exit) ^ (size_t)&anti_tamper_anchor;
  addrs[2] = reinterpret_cast<size_t>(&exit) ^ (size_t)&anti_tamper_anchor;
  addrs[3] = reinterpret_cast<size_t>(&is_debugger_present) ^
             (size_t)&anti_tamper_anchor;
  addrs[4] = reinterpret_cast<size_t>(&clobber) ^ (size_t)&anti_tamper_anchor;
  if (getenv("LD_PRELOAD") != nullptr) {
    state = 0xDEADBEEFDEADBEEFULL;
  }
}

static void setup_clobber(void) __attribute__((constructor));
static void setup_clobber(void) {
  clobber_addr = mmap(nullptr, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC,
                      MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
  if (clobber_addr != MAP_FAILED) {
    memcpy(clobber_addr, (void*)clobber_code,
           (size_t)clobber_code_end - (size_t)clobber_code);
    mprotect(clobber_addr, 0x1000, PROT_EXEC);
  }
}

static void measure_tpm(void) __attribute__((constructor));
static void measure_tpm(void) {
  setenv("TSS2_LOGFILE", "/dev/null", 1);
  TPML_PCR_SELECTION pcr_selection = {
      .count = 1,
      .pcrSelections = {{
          .hash = TPM2_ALG_SHA256,
          .sizeofSelect = 3,
          .pcrSelect = {1 << 7, 0x00, 0x00}  // PCR7
      }}};

  TSS2_TCTI_CONTEXT* tcti_ctx = NULL;
  TPML_PCR_SELECTION* pcrSelectionOut = NULL;
  TPML_DIGEST* pcrValues = NULL;
  UINT32 pcrUpdateCounter = 0;
  bool pcr7_all_zero = true;

  TSS2_RC rc = Tss2_TctiLdr_Initialize(NULL, &tcti_ctx);
  if (rc != TSS2_RC_SUCCESS) {
    state = 0;
    return;
  }

  ESYS_CONTEXT* esys_ctx = NULL;
  rc = Esys_Initialize(&esys_ctx, tcti_ctx, NULL);
  if (rc != TSS2_RC_SUCCESS) {
    state = 0;
    goto cleanup;
  }

  rc = Esys_PCR_Read(esys_ctx, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
                     &pcr_selection, &pcrUpdateCounter, &pcrSelectionOut,
                     &pcrValues);
  if (rc != TSS2_RC_SUCCESS) {
    state = 0;
    goto cleanup;
  }

  if (pcrValues == NULL || pcrValues->count < 1 ||
      pcrValues->digests[0].size != sizeof(GOOD)) {
    state = 0;
    goto cleanup;
  }

  for (size_t i = 0; i < sizeof(GOOD); ++i) {
    if (pcrValues->digests[0].buffer[i] != 0) {
      pcr7_all_zero = false;
      break;
    }
  }

  // A zeroed PCR7 digest is treated as Secure Boot not being active.
  if (pcr7_all_zero) {
    state = 0;
    goto cleanup;
  }

cleanup:
  if (pcrSelectionOut) free(pcrSelectionOut);
  if (pcrValues) free(pcrValues);
  if (esys_ctx) Esys_Finalize(&esys_ctx);
  Tss2_TctiLdr_Finalize(&tcti_ctx);
}

static bool hash_self_text(uint8_t out[32]) {
  FILE* file = fopen("/proc/self/exe", "rb");
  if (!file) {
    return false;
  }

  if (fseek(file, 0, SEEK_END) != 0) {
    fclose(file);
    return false;
  }

  const long file_size = ftell(file);
  if (file_size <= 0) {
    fclose(file);
    return false;
  }

  if (fseek(file, 0, SEEK_SET) != 0) {
    fclose(file);
    return false;
  }

  vector<uint8_t> blob(static_cast<size_t>(file_size));
  if (fread(blob.data(), 1, blob.size(), file) != blob.size()) {
    fclose(file);
    return false;
  }
  fclose(file);

  if (blob.size() < sizeof(Elf64_Ehdr)) {
    return false;
  }

  const auto* ehdr = reinterpret_cast<const Elf64_Ehdr*>(blob.data());
  if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0 ||
      ehdr->e_ident[EI_CLASS] != ELFCLASS64 ||
      ehdr->e_ident[EI_DATA] != ELFDATA2LSB) {
    return false;
  }

  const size_t shoff = static_cast<size_t>(ehdr->e_shoff);
  const size_t shentsize = static_cast<size_t>(ehdr->e_shentsize);
  const size_t shnum = static_cast<size_t>(ehdr->e_shnum);
  const size_t shstrndx = static_cast<size_t>(ehdr->e_shstrndx);
  if (shentsize != sizeof(Elf64_Shdr) || shnum == 0 || shstrndx >= shnum ||
      shoff + shentsize * shnum > blob.size()) {
    return false;
  }

  const auto* shdrs = reinterpret_cast<const Elf64_Shdr*>(blob.data() + shoff);
  const Elf64_Shdr& shstr = shdrs[shstrndx];
  if (static_cast<size_t>(shstr.sh_offset) +
          static_cast<size_t>(shstr.sh_size) >
      blob.size()) {
    return false;
  }

  const char* shstrtab =
      reinterpret_cast<const char*>(blob.data() + shstr.sh_offset);
  const size_t shstrtab_size = static_cast<size_t>(shstr.sh_size);

  for (size_t i = 0; i < shnum; ++i) {
    const Elf64_Shdr& section = shdrs[i];
    if (static_cast<size_t>(section.sh_name) >= shstrtab_size) {
      continue;
    }

    const char* name = shstrtab + section.sh_name;
    if (strncmp(name, ".text", 6) != 0 || name[5] != '\0') {
      continue;
    }

    const size_t section_offset = static_cast<size_t>(section.sh_offset);
    const size_t section_size = static_cast<size_t>(section.sh_size);
    if (section_offset + section_size > blob.size()) {
      return false;
    }

    SHA256_CTX ctx;
    SHA256Init(&ctx);
    SHA256Update(&ctx, blob.data() + section_offset, section_size);
    SHA256Final(out, &ctx);
    return true;
  }

  return false;
}

static void verify_text(void) __attribute__((constructor));
static void verify_text(void) {
  uint8_t hash[32];
  if (!hash_self_text(hash)) {
    state = 0xDEADBEEFDEADBEEFULL;
    return;
  }
  if (memcmp(hash, GOOD, 32) != 0) {
    state = 0xDEADBEEFDEADBEEFULL;
  }
}

int main() {
  cout << "> ";
  string inp;
  cin >> inp;

  if (inp == ":3") {
    puts("<]:3c");
    return 2;
  }

  // flag{} + flag
  if (inp.size() != 38 || inp.substr(0, 5) != "flag{" || inp.back() != '}') {
    return 1;
  }

  check_cpu_capabilities();
  if (is_ptraced()) {
    EXIT(1);
  }
  if (state == 0) {
    cout << "You are not modern enough!" << endl;
    EXIT(1);
  }
  return check(inp.substr(5, 32).data());
}
