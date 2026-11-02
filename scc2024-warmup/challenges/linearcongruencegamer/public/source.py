from random import randint

# Hey, Gamer, I was making a randomness generator, it goes like this
class LCG:
    def __init__(self):
        self.mod = 8471050156910645297199092184997948739352218102032175415195952882946019032523893352683847323674258073
        self.inc = randint(0, self.mod-1)
        self.mul = randint(0, self.mod-1)
        self.state = randint(0, self.mod-1)

    def next(self):
        self.state = ( self.mul * self.state + self.inc ) % self.mod
        return self.state
    
    def encrypt(self, msg: bytes):
        self.next()
        bstate = self.state.to_bytes(len(msg)*2, byteorder='big')
        return [x^y for x,y in zip(msg, bstate)] # XOR with the state!

# and I instantiated it
lcg = LCG()
# ran it a few times...
outs = [lcg.next() for _ in range(20)]
print(outs)

# but encrypted the flag...
from SECRET import FLAG
print(lcg.encrypt(FLAG))

# Can you help me recover the flag?