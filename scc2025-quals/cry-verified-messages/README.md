# CRY - Verify Message
**Author** : Pimpest  
**Difficulty**: Easy  
**Description**: Please speak with an admin if you see this message

**Flag**: ``SCC{4dmin_4sked_m3_wh4ts_a_P0p_g4dg3t__321_sk1d}``

# Writeup

You can generate a keypair using a small private key and then you can brute force $\varphi(N)$   knowing that $$\varphi(N) = \left\lfloor\frac{(pubKey*privKey)-1}{i}\right\rfloor$$ for some integer $i$ where $0<i<privKey$