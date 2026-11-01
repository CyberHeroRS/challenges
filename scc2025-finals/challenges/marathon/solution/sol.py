# Extract the matrix coeffs from source
pattern = """
    sprintf(buf, op2_fmt, FLAG, 0, &R3);
    sprintf(buf, op4_fmt, &R1, op4_bit, R2, 0, R1, 0, &R3);
    sprintf(op4_fmt, op4_backup);
    sprintf(buf, op2_fmt, R3, 0, &R1);
    sprintf(buf, op3_fmt, 251);
    sprintf(buf, op3_fmt, R1);
    sprintf(buf+251+1, "");
    sprintf(buf, op4_fmt, buf+251, op4_bit, R1, 0, 65283, 0, &R1);
    sprintf(op4_fmt, op4_backup);"""

key = "sprintf(buf, op2_fmt, FLAG, 0, &R3);"
sep = "sprintf(buf, op1_fmt, FLAG, 0, 0xfffe, 0, &R2);"
end = "R1=0, FLAG=0, R2=0, R3=0;"

M = []
with open("public/source.c", "r") as src:
    coeff = 0
    row = []
    for line in src:
        if key in line:
            coeff += 1
        elif sep in line:
            row.append(coeff)
            coeff = 0
        elif end in line:
            row.append(coeff)
            coeff = 0
            M.append(row)
            row = []
    row.append(coeff)
    M.append(row)
    for row in M:
        del row[0]

x = []
with open("public/output.txt", "r") as vec:
    x = [int(i) for i in vec.readline().split()]

n = len(M)
assert n == len(x)
assert n == len(M[0])
mod = 251

# You should use z3 or at least numpy for this, but just to illustrate.

# Gaussian elimination over Z_251
for i in range(n):
    # Set the diagonal elt. to 1
    modinv = pow(M[i][i], -1, mod)
    M[i] = [(modinv * x) % mod for x in M[i]]
    x[i] = modinv * x[i] % mod

    # Kill all the elts below
    for j in range(i+1, n):
        coeff = M[j][i]
        for k in range(i, n):
            M[j][k] = (M[j][k] - (coeff * M[i][k] % mod)) % mod
        x[j] = (x[j] - (coeff * x[i] % mod)) % mod

# Back to kill elements above
for d in range(n):
    i = n - d - 1
    for dd in range(d+1, n):
        j = n - dd - 1
        coeff = M[j][i]
        x[j] = (x[j] - (coeff*x[i]%mod)) % mod

flag = [chr(c) for c in x]
# Magic
print("".join(flag))
