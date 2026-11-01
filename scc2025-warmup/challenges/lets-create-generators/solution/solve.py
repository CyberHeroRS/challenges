outs = []
with open("./out.txt", "r") as f:
    for line in f.readlines():
        v = int(line)
        outs.append(v)

# A = B * C + D
print(outs)
p = 173645114154668217364539488402951813100695540623483900609
a = 17
left = outs[1]
left = left - a # A - D = B * C
left = left * pow(outs[0], -1, p)
mul = (left) % p
print(mul)
flag = ( (outs[0] - a) * pow(mul, -1, p) ) % p
print(int.to_bytes(flag, length=20, byteorder="big"))