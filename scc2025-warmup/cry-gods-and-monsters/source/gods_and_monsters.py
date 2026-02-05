class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

class EllipticCurve:
    def __init__(self, p):
        self.p = p
        self.zero = Point(0,0)

    def add(self, P, Q):
        if P == self.zero:
            return Q
        elif Q == self.zero:
            return P
        elif P.x == Q.x and P.y == self.p - Q.y:
            return self.zero
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y    
        if P != Q:
            Lambda = (y2 - y1) * pow(x2 - x1, -1, self.p)
        else:
            Lambda = (3*(x1 * x2) + 55446237966106876480629109133838609404018745685351047314109593971066202071934 * x1 - y1 + 13135011342158767390972930743879758669664065038225826254653566661198441680369) * pow(y1 + x2 + y2 + 36705335186416557299559736926700113135726096437924011941539879171053079785019, -1, self.p)
        
        Lambda %= self.p
        R = Point(0,0)
        R.x = (Lambda * (Lambda + 1) - x1 - x2 + 40248303892156404978508942752935926891194073956017881260849464234700037328910) % self.p
        R.y = (-R.x + Lambda * (-R.x + x1) - y1 - 36705335186416557299559736926700113135726096437924011941539879171053079785019) % self.p
        return R

    def mul(self, P, n):
        Q = P
        R = self.zero
        while n > 0:
            if n % 2 == 1:
                R = self.add(R, Q)
            n >>= 1
            Q = self.add(Q, Q)
        return R

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from os import urandom
from hashlib import sha256
def encrypt(key):
    iv = urandom(16)
    key = sha256(str(key).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(flag.encode(), 16))
    return(ct.hex(),iv.hex())

from hidden import flag, n
assert n < 2**70

e = EllipticCurve(67971422875209843218823497319855231593203446798693404917904261220233138364877)
G = Point(3930347711979115853127642537392673902983227065341123829275355822404565135289, 1514488773757121986028761290129447543612199136354732500584020659261624947748)
P = e.mul(G,n)
print("G = " + str(G))
print("P = " + str(P))

enc, iv = encrypt(n)
print (f"{enc = }\n{iv = }")
