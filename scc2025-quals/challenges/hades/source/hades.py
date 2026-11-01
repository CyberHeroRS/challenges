from Crypto.Cipher import AES
from os import urandom
import random
import binascii

flag = open("flag.txt", "rb").read()

class NextGenPRF:
    def __init__(self, option):
        self.key = urandom(16)
        # 1 = pseudorandom, 0 = true random
        self.option = option
    
    def pseudorandom(self, msg): # pseudorandom function
        cipher = AES.new(self.key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(msg)
        return ciphertext
    
    def true_random(self, msg):
        random_string = urandom(32)
        return bytes(rs ^ m for rs, m in zip(random_string, msg))
    
    def oracle(self, msg):
        if (len(msg) != 16):
            return None
        if (self.option == 0):
            return self.true_random(msg)
        else:
            return self.pseudorandom(msg)
    
    def guess(self, mode_guess):
        return (self.option == mode_guess)


def judgement(questions_left, left_soul, right_soul):
    while True:
        if (questions_left == 0):
            break
        print("State your question for the souls: ", end="")
        hex_message = input()
        try:
            message = binascii.unhexlify(hex_message)
        except binascii.Error:
            continue
        if (len(message) != 16):
            continue
        left_response = binascii.hexlify(left_soul.oracle(message)).decode("utf-8")
        right_response = binascii.hexlify(right_soul.oracle(message)).decode("utf-8")
        print(f"The left soul screams: {left_response}")
        print(f"The right soul screams: {right_response}")
        return (questions_left - 1)

BANNER = """
   ___   _   __  __ ___   
  / __| /_\ |  \/  | __|  
 | (_ |/ _ \| |\/| | _|   
  \___/_/_\_\_|  |_|___|  
  / _ \| __|              
 | (_) | _|               
  \___/|_|   ___  ___ ___ 
 | || | /_\ |   \| __/ __|
 | __ |/ _ \| |) | _|\__ \ 
 |_||_/_/ \_\___/|___|___/
                          
\n\n\n
"""
NYX_HEADER = """
|\ | \ / \_/ 
| \|  |  / \ 
"""
INTRO_TEXT = """
/   Zagreus, my child, are you there?
|   
|   I have discussed the matter of your escapes with your Father, and
|   I believe we have reached an agreement. There exist souls even He
|   has been unable to judge. They're deceivers, sent by Olympus, and
|   have blocked the intake of new souls. Tell apart the real from the
\   fake, and your Father may let you in on a family treasure.
"""
FAIL = """
...the light fades. Back to the pool of blood you go.
"""
SUCCESS = """
Soul vanquished.
"""
WIN_TEXT = """
/   Wonderful work.
|   
|   I knew you could do it. Here, have this. You Father kept it hidden
\   exceptionally well.
"""
def main():
    souls = 52
    questions = 100
    print(BANNER)
    print(NYX_HEADER)
    print(INTRO_TEXT)
    while (souls > 0):
        truth = random.getrandbits(1) # 0 is left, 1 is right
        if (truth == 0):
            left = NextGenPRF(0) # true random
            right = NextGenPRF(1) # pseudorandom
        else:
            left = NextGenPRF(1) # pseudorandom
            right = NextGenPRF(0) # true random
        
        while True:
            print("> ", end="")
            decision = input()
            match decision:
                case "1": # left door
                    if (left.guess(0)):
                        print(SUCCESS)
                        souls -= 1
                        break
                    else:
                        print(FAIL)
                        return
                case "2": # right door
                    if (right.guess(0)):
                        print(SUCCESS)
                        souls -= 1
                        break
                    else:
                        print(FAIL)
                        return
                case "3":
                    if questions == 0:
                        print(FAIL)
                        return
                    questions = judgement(questions, left, right)
    
    print(NYX_HEADER)
    print(WIN_TEXT)
    print(flag)

if (__name__ == "__main__"):
    main()
