import os
from Crypto.Hash import CMAC
from Crypto.Cipher import DES3

KEY = bytes.fromhex(os.environ.get('KEY', '000000000000000000000000000000000000000000000000'))
assert bytes.fromhex('7DB0D37DF936C550') == CMAC.new(KEY, ciphermod=DES3).digest()
FLAG = os.environ.get('FLAG', 'SCC{test}')
TAG = bytes.fromhex(os.environ.get('TAG', 'FFFFFFFFFFFFFFFF'))

i = bytes.fromhex(input('uploading new firmware...\n'))
signature = i[:128]
public_key = i[128:256]
code = i[256:]
prefix = b'\0\1' + b'\xff' * (128-3-8) + b'\0'
e = 65537
assert public_key[0] & 128 and public_key[-1] & 1
N = int.from_bytes(public_key)
assert TAG == CMAC.new(KEY, ciphermod=DES3).update(public_key).digest()
assert prefix + CMAC.new(KEY, ciphermod=DES3).update(code).digest() == pow(int.from_bytes(signature), e, N).to_bytes(128)
eval(code.decode())
