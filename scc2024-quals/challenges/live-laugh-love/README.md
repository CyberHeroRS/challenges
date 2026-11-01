# Live Laugh Love

**Author** : Lofer  
**Difficulty** : <font color='red'>Hard</font>  
**Description**: 
"Live Laugh Love" is the official slogan of the Poly2585 hash family. Fast hashing, now with NSA-approved key deriving. 

Flag: `SCC{sh0rt_FL4g!}`

## Solution

The challenge first relies on finding a collision of `r` and `s` values between the flag's and a target message's hash. This is done by having the submitted keys differ only in the 8th bits (which DES doesn't use, the so-called "parity bits").

The second half of the challenge revolves around using lattices to find the flag. Some light brute-force is requires due to the mod 2^256 reduction in the hash function. The following is the lattice that extracts the flag, for a correct r, s, and pre-reduction hash value:
```py
m = [[0 for _ in range(18)] for _ in range(18)]

FF = Zmod(2^258-5)
m[0][0] = - int(FF(hash) - s)

m[1][0] = 2^258 - 5
m[1][1] = 1

for i in range(2, 18):
    m[i][i] = 1
    m[i][0] = - int(FF((r)^(i-1)))

m = Matrix(ZZ, m)
flag = m.LLL()[0]
```
