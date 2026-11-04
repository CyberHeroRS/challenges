from os import environ
from secrets import randbelow
from hashlib import sha256

FLAG = environ.get('FLAG', 'SCC{test}').encode()

p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
order = 115792089210356248762697446949407573529996955224135760342422259061068512044369
a = -3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
size = 32

# do not worry add and double procedures work as intended :)
def add(p, a, X1, Y1, Z1, X2, Y2, Z2):
    U1 = (X1*Z2) % p
    U2 = (X2*Z1) % p
    S1 = (Y1*Z2) % p
    S2 = (Y2*Z1) % p
    ZZ = (Z1*Z2) % p
    T = (U1+U2) % p
    TT = (T*T) % p
    M = (S1+S2) % p
    t0 = (ZZ*ZZ) % p
    t1 = (a*t0) % p
    t2 = (U1*U2) % p
    t3 = (TT-t2) % p
    R = (t3+t1) % p
    F = (ZZ*M) % p
    L = (M*F) % p
    LL = (L*L) % p
    t4 = (T+L) % p
    t5 = (t4*t4) % p
    t6 = (t5-TT) % p
    G = (t6-LL) % p
    t7 = (R*R) % p
    t8 = (2*t7) % p
    W = (t8-G) % p
    t9 = (F*W) % p
    X3 = (2*t9) % p
    t10 = (2*W) % p
    t11 = (G-t10) % p
    t12 = (2*LL) % p
    t13 = (R*t11) % p
    Y3 = (t13-t12) % p
    t14 = (F*F) % p
    t15 = (F*t14) % p
    Z3 = (4*t15) % p
    return (X3, Y3, Z3)

def double(p, a, X1, Y1, Z1):
    XX = (X1*X1) % p
    ZZ = (Z1*Z1) % p
    t0 = (3*XX) % p
    t1 = (a*ZZ) % p
    w = (t1+t0) % p
    t2 = (Y1*Z1) % p
    s = (2*t2) % p
    ss = (s*s) % p
    sss = (s*ss) % p
    R = (Y1*s) % p
    RR = (R*R) % p
    t3 = (X1+R) % p
    t4 = (t3*t3) % p
    t5 = (t4-XX) % p
    B = (t5-RR) % p
    t6 = (w*w) % p
    t7 = (2*B) % p
    h = (t6-t7) % p
    X3 = (h*s) % p
    t8 = (B-h) % p
    t9 = (2*RR) % p
    t10 = (w*t8) % p
    Y3 = (t10-t9) % p
    Z3 = sss
    return X3, Y3, Z3

def multiply(p, a, X1, Y1, Z1, scalar):
    X2, Y2, Z2 = X1, Y1, Z1
    for i in range(scalar.bit_length()-2, -1, -1):
        X2, Y2, Z2 = double(p, a, X2, Y2, Z2)
        # X2, Y2, Z2 = add(p, a, X2, Y2, Z2, X2, Y2, Z2) # this can replace double
        if scalar & (1 << i):
            X2, Y2, Z2 = add(p, a, X1, Y1, Z1, X2, Y2, Z2)
    return X2, Y2, Z2

class SmartCard():
    
    def __init__(sc, pin):
        print('Initializing ...')
        sc.d = randbelow(order)
        print(f'Card fingerprint: {int.from_bytes(sha256(sc.d.to_bytes(size)).digest()) ^ int.from_bytes(FLAG)}')
        sc.pin = pin

    def export_public_key(sc):
        return multiply(p, a, Gx, Gy, 1, pow(sc.d, -1, order))
    
    def sign(sc, pin, m):
        if m >= order or pin < 0 or pin >= 10**20: return
        k = randbelow(order)
        zero = sc.pin - pin
        x, y, z = multiply(p + zero, a + zero, Gx + zero, Gy + zero, 1 + zero, k + zero)
        r = int.from_bytes(sha256(x.to_bytes(size) + y.to_bytes(size) + z.to_bytes(size)).digest())
        s = (k + (r ^ m)) * sc.d % order
        return x, y, z, s,# k


sc = SmartCard(pin=randbelow(10**20))
# Surely the pin is 1234.
print(sc.sign(pin=1234, m=int.from_bytes(sha256(b'I urgently need 9000 EUR.').digest())))
print(sc.sign(pin=1234, m=int.from_bytes(sha256(b'Here the the address bc1q8pk09x284z5dm4juzwxvhrd9a84qkaptse2y0m.').digest())))
# Legend has it that if you send money to this addres, you will receive the flag :).