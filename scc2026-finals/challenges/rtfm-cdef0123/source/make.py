from Crypto.Hash import CMAC
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Util.number import isPrime
with open('keypair.pem', 'rb') as key_file:
    private_key = RSA.import_key(key_file.read())

# https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/TDES_CMAC.pdf
KEY = bytes.fromhex('0123456789ABCDEF23456789ABCDEF01456789ABCDEF0123')
assert bytes.fromhex('7DB0D37DF936C550') == CMAC.new(KEY, ciphermod=DES3).digest()
TAG = CMAC.new(KEY, ciphermod=DES3).update(private_key.n.to_bytes(128)).digest()

print(f'KEY = {KEY.hex().upper()}')
print(f'TAG = {TAG.hex().upper()}')

def sign(message, d, n):
    # 0x00 || 0x01 || PS || 0x00 || T
    prefix = b'\0\1' + b'\xff' * (128-3-8) + b'\0'
    x = int.from_bytes(prefix + CMAC.new(KEY, ciphermod=DES3).update(message).digest())
    return pow(x, d, n).to_bytes(128)

code = b'print("hello from the other side")'
signed_firmware = bytes.fromhex((sign(code, private_key.d, private_key.n) + private_key.n.to_bytes(128) + code).hex())

with open('signed_firmware.bin', 'wb') as f:
    f.write(signed_firmware)
    print('signed_firmware.bin has been generated')