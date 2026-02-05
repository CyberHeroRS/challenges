from hidden import mul, inc, flag

class LCG:
    def __init__(self, mul, inc, mod):
        self.p = mod
        self.m = mul
        self.a = inc
        self.state = flag
    
    def next(self):
        self.state = (self.state * self.m + self.a) % self.p
        return self.state
    
lcg = LCG(mul, inc, 110500871926380516645177079188266723643672120737022174485551617105252447993793)

for _ in range(5):
    print(lcg.next())