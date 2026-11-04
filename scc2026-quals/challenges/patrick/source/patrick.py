from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Random import get_random_bytes
from os import getenv

FLAG = getenv("FLAG") or "SCC{test}"

class Patrick:
    def __init__(self, key1, key2, key3):
        self.key1 = key1[:16]
        self.key2 = key2[:16]
        self.key3 = key3[:16]
        self.block_size = 3 # 24 bits ought to be enough for anyone!
        self.state = bytes(self.block_size)

    def absorb_block(self, block):
        self.state = bytes(a ^ b for a, b in zip(self.state, block))
        cipher = AES.new(self.key1, AES.MODE_ECB)
        self.state = cipher.encrypt(pad(self.state, AES.block_size))[:self.block_size]

    def absorb(self, plaintext):
        for i in range(0, len(plaintext), self.block_size):
            block = plaintext[i:i + self.block_size]
            if len(block) < self.block_size:
                block = pad(block, self.block_size)
            self.absorb_block(block)

    def finalize(self):
        cipher = AES.new(self.key1, AES.MODE_ECB)
        self.state = cipher.encrypt(pad(self.state, AES.block_size))
        
        cipher = AES.new(self.key2, AES.MODE_ECB)
        self.state = cipher.decrypt(self.state)
        
        cipher = AES.new(self.key3, AES.MODE_ECB)
        tag = cipher.encrypt(self.state)
        
        self.state = bytes(self.block_size)
        return tag

def main():
    key1 = get_random_bytes(3).hex() * 2 + "KEY1"
    key2 = get_random_bytes(3).hex() * 2 + "KEY2"
    key3 = get_random_bytes(3).hex() * 2 + "KEY3"
    
    cipher = Patrick(key1.encode(), key2.encode(), key3.encode())
    cipher.absorb(b"spongebob")
    target_tag = cipher.finalize().hex()
    
    print("Ahoy! Who lives in a pineapple under the sea? (hex input)")
    while True:
        data = input().strip()
        data = bytes.fromhex(data)
        if b"spongebob" in data:
            print("Correct! But are you Spongebob? (hex input)")
            tag = input().strip() 
            if tag == target_tag:
                print(FLAG)
                exit()
            else:
                print("Oh, I guess not...")
        else:
            cipher.absorb(data)
            tag = cipher.finalize()
            print(tag.hex())
    

if __name__ == "__main__":
    main()
