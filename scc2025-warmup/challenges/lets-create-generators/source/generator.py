from hidden import mul, flag

class LCG:
    def __init__(self, mul, inc, mod):
        self.p = mod
        self.m = mul
        self.a = inc
        self.state = flag
    
    def next(self):
        self.state = (self.state * self.m + self.a) % self.p
        return self.state
    
lcg = LCG(mul, 17, 173645114154668217364539488402951813100695540623483900609)

for _ in range(5):
    print(lcg.next())