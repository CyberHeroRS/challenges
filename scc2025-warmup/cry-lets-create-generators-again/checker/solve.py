outs = []
with open("./out.txt", "r") as f:
    for line in f.readlines():
        v = int(line)
        outs.append(v)

p = 110500871926380516645177079188266723643672120737022174485551617105252447993793

x0 = outs[0]
x1 = outs[1]
x2 = outs[2]
mul = (x2 - x1) * pow(x1 - x0, -1, p) % p
print(mul)
# A = B * C + D

inc = (x1 - mul * x0) % p

flag = ( (outs[0] - inc) * pow(mul, -1, p) ) % p
print(int.to_bytes(flag, length=32, byteorder="big"))