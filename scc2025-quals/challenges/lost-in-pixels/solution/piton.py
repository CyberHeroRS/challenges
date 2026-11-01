x = [int(i, 16) for i in open("./file", "r").read().split(" ")]

for i in range(len(x)):
    if i != 0 and x[i] == x[i - 1] == 0:
        continue
    print(format(x[i], '08b').replace('0', ' ').replace('1', '#'), end="")
    print()
