#include <cstdint>

#include <debugging>
#if __has_include(<simd>)
#include <simd>
namespace sx = std;
#elif __has_include(<experimental/simd>)
#include <experimental/simd>
namespace sx = std::experimental;
#else
#error "No std::simd support"
#endif

uint64_t FLAG[] = {0}; /*__FLAG__*/

using U64x4 = sx::fixed_size_simd<uint64_t, 4>;
using U32x16 = sx::fixed_size_simd<uint32_t, 16>;

static inline __attribute__((always_inline)) U64x4 make_u64x4(uint64_t w0,
                                                              uint64_t w1,
                                                              uint64_t w2,
                                                              uint64_t w3) {
  U64x4 v(0);
  if (is_debugger_present()) {
    w2 += 133713371337ULL;
  }
  v[0] = w0;
  v[1] = w1;
  v[2] = w2;
  v[3] = w3;
  return v;
}

static inline __attribute__((always_inline)) U32x16
make_u32x16(uint32_t v0, uint32_t v1, uint32_t v2, uint32_t v3, uint32_t v4,
            uint32_t v5, uint32_t v6, uint32_t v7, uint32_t v8, uint32_t v9,
            uint32_t v10, uint32_t v11, uint32_t v12, uint32_t v13,
            uint32_t v14, uint32_t v15) {
  U32x16 v(0);
  if (is_debugger_present()) {
    v1 += 1;
    v14 = 1;
  }
  v[0] = v0;
  v[1] = v1;
  v[2] = v2;
  v[3] = v3;
  v[4] = v4;
  v[5] = v5;
  v[6] = v6;
  v[7] = v7;
  v[8] = v8;
  v[9] = v9;
  v[10] = v10;
  v[11] = v11;
  v[12] = v12;
  v[13] = v13;
  v[14] = v14;
  v[15] = v15;
  return v;
}

static inline __attribute__((always_inline)) U32x16 unpack_words(U64x4 s) {
  const uint64_t a0 = s[0];
  const uint64_t a1 = s[1];
  const uint64_t a2 = s[2];
  const uint64_t a3 = s[3];
  return make_u32x16(static_cast<uint32_t>((a0 >> 0) & 0xFFFFULL),
                     static_cast<uint32_t>((a0 >> 16) & 0xFFFFULL),
                     static_cast<uint32_t>((a0 >> 32) & 0xFFFFULL),
                     static_cast<uint32_t>((a0 >> 48) & 0xFFFFULL),
                     static_cast<uint32_t>((a1 >> 0) & 0xFFFFULL),
                     static_cast<uint32_t>((a1 >> 16) & 0xFFFFULL),
                     static_cast<uint32_t>((a1 >> 32) & 0xFFFFULL),
                     static_cast<uint32_t>((a1 >> 48) & 0xFFFFULL),
                     static_cast<uint32_t>((a2 >> 0) & 0xFFFFULL),
                     static_cast<uint32_t>((a2 >> 16) & 0xFFFFULL),
                     static_cast<uint32_t>((a2 >> 32) & 0xFFFFULL),
                     static_cast<uint32_t>((a2 >> 48) & 0xFFFFULL),
                     static_cast<uint32_t>((a3 >> 0) & 0xFFFFULL),
                     static_cast<uint32_t>((a3 >> 16) & 0xFFFFULL),
                     static_cast<uint32_t>((a3 >> 32) & 0xFFFFULL),
                     static_cast<uint32_t>((a3 >> 48) & 0xFFFFULL));
}

template <int Delta>
static inline __attribute__((always_inline)) U64x4 delta_swap64(U64x4 x,
                                                                U64x4 mask) {
  const auto t = ((x >> Delta) ^ x) & mask;
  return x ^ t ^ (t << Delta);
}

static inline __attribute__((always_inline)) U64x4 cross_swap64(U64x4 s,
                                                                U64x4 mask) {
  const auto swapped = make_u64x4(s[1], s[0], s[3], s[2]);
  return (s & ~mask) | (swapped & mask);
}

static inline __attribute__((always_inline)) U64x4 cross_swap128(U64x4 s,
                                                                 U64x4 mask) {
  const auto swapped = make_u64x4(s[2], s[3], s[0], s[1]);
  return (s & ~mask) | (swapped & mask);
}

static inline __attribute__((always_inline)) U64x4 apply_permutation(U64x4 s) {
  /*__PERM_STAGES__*/
  return s;
}
