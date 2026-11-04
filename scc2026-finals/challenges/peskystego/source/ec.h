#ifndef EC_H
#define EC_H

#include <stdint.h>

#define EC_P 4294967291ULL  /* 2^32 - 5 (prime) */
#define EC_A 1ULL
#define EC_B 44ULL

typedef struct {
  uint64_t x;
  uint64_t y;
  int inf;
} ECPoint;

static inline uint64_t ec_mulmod(uint64_t a, uint64_t b) {
  __uint128_t product = (__uint128_t)a * b;
  return (uint64_t)(product % EC_P);
}

static inline uint64_t ec_inv(uint64_t a) {
  uint64_t result = 1, base = a % EC_P, exp = EC_P - 2;
  while (exp) {
    if (exp & 1) result = ec_mulmod(result, base);
    base = ec_mulmod(base, base);
    exp >>= 1;
  }
  return result;
}

static inline ECPoint ec_add(ECPoint P, ECPoint Q) {
  if (P.inf) return Q;
  if (Q.inf) return P;

  uint64_t lam;
  if (P.x == Q.x) {
    if (P.y != Q.y) return (ECPoint){0, 0, 1};
    uint64_t num = (3 * ec_mulmod(P.x, P.x) + EC_A) % EC_P;
    uint64_t den = 2 * P.y % EC_P;
    lam = ec_mulmod(num, ec_inv(den));
  } else {
    uint64_t dy = (Q.y + EC_P - P.y) % EC_P;
    uint64_t dx = (Q.x + EC_P - P.x) % EC_P;
    lam = ec_mulmod(dy, ec_inv(dx));
  }

  uint64_t rx = (ec_mulmod(lam, lam) + 2 * EC_P - P.x - Q.x) % EC_P;
  uint64_t ry =
      (ec_mulmod(lam, (P.x + EC_P - rx) % EC_P) + EC_P - P.y) % EC_P;
  return (ECPoint){rx, ry, 0};
}

static inline ECPoint ec_generator(void) {
  for (uint64_t x = 1; x < EC_P; x++) {
    uint64_t rhs =
        (ec_mulmod(ec_mulmod(x, x), x) + ec_mulmod(EC_A, x) + EC_B) % EC_P;
    uint64_t y = 1, base = rhs, exp = (EC_P + 1) / 4;
    while (exp) {
      if (exp & 1) y = ec_mulmod(y, base);
      base = ec_mulmod(base, base);
      exp >>= 1;
    }
    if (ec_mulmod(y, y) == rhs) return (ECPoint){x, y, 0};
  }
  return (ECPoint){0, 0, 1};
}

static inline ECPoint ec_mul(ECPoint P, uint64_t k) {
  ECPoint result = {0, 0, 1};
  while (k) {
    if (k & 1) result = ec_add(result, P);
    P = ec_add(P, P);
    k >>= 1;
  }
  return result;
}

#endif
