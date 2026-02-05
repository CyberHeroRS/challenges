from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from gmpy2 import mpz, lcm, iroot
from time import time
from tqdm import tqdm
from sys import set_int_max_str_digits
set_int_max_str_digits(1000_000)

FLAG = b'SCC{???????????????????????????????????????????????????}'
e = 3

with open('public/output.txt', 'r') as f:
    lines = f.readlines()
    p = mpz(lines[0].split('=')[1])
    N = mpz(lines[1].split('=')[1])
    c = mpz(lines[2].split('=')[1])
    ct = bytes.fromhex(lines[3].split('=')[1])

    l = 4096
    q = iroot(N//p, l)[0]
    print(f'q = {q}')

    d = pow(e, -1, lcm(p-1, q-1))
    d_p = d % (p-1)
    d_q = d % (q-1)
    m_p = pow(c, d_p, p)
    m_q = pow(c, d_q, q)

    m_q_ = pow(c, d_q-1, q)
    m_qi = m_q
    q3i = pow(e, -1, q)
    qi1 = q*q
    for i in tqdm(range(1, l)):
        x = (c % qi1) - pow(m_qi, e, qi1) 
        y = ((x*m_q_) % qi1) * q3i % qi1
        m_qi += y
        qi1 *= q

    t = time()
    ql = q**l
    m_ = (m_p + p * ((m_qi - m_p) * pow(p, -1, ql) % ql))
    print(f'done in {(time()-t):0.2f}s.')

    def dec(m_):
        K = int(m_).to_bytes(N.bit_length()//8, "big")
        key, iv = K[-16:], K[-32:-16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), 16)
        if b'SCC{' in pt:
            print(pt)
            return pt
    
    dec(m_) or dec(m_ + N)


