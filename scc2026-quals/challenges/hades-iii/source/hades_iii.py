from Crypto.Cipher import AES
from os import urandom, getenv
import random
import binascii

flag = getenv("FLAG") or "SCC{test}"
KEY = urandom(16)

class NextGenPRF:
    def __init__(self, option):
        self.key = KEY
        self.g = 17
        self.p = 8056155217297667024640676103489388132749565410810114417324337594619262050521095735634369412853881198743766882674233588531999412443768385413663901114403961
        # 1 = pseudorandom, 0 = true random
        self.option = option
    
    def pseudorandom(self, msg: bytes): # pseudorandom function
        m1, m2 = msg[:16], msg[16:]
        cipher = AES.new(self.key, AES.MODE_ECB)
        
        a, b = cipher.encrypt(m1), cipher.encrypt(m2)
        c = int(a.hex(), 16)**2 * int(b.hex(), 16)
        return pow(self.g, c, self.p)
        
    def true_random(self, msg):
        random_number = random.randrange(0, self.p)
        return random_number
    
    def oracle(self, msg):
        if (len(msg) != 32):
            return None
        if (self.option == 0):
            return self.true_random(msg)
        else:
            return self.pseudorandom(msg)
    
    def guess(self, mode_guess):
        return (self.option == mode_guess)


seen = set()
def judgement(questions_left, left_soul, right_soul):
    global seen
    while True:
        if (questions_left == 0):
            break
        print("State your question for the souls: ", end="")
        hex_message = input()
        try:
            message = binascii.unhexlify(hex_message)
        except binascii.Error:
            continue
        if (len(message) != 32):
            continue
        if message in seen:
            continue
        seen.add(message)
        left_response = left_soul.oracle(message)
        right_response = right_soul.oracle(message)
        print(f"The left soul screams: {left_response}")
        print(f"The right soul screeches: {right_response}")
        return (questions_left - 1)

BANNER = """
   ___   _   __  __ ___             
  / __| /_\ |  \/  | __|            
 | (_ |/ _ \| |\/| | _|             
  \___/_/_\_\_|  |_|___|            
  / _ \| __|                        
 | (_) | _|                         
  \___/|_|   ___  ___ ___   ___ ___ ___
 | || | /_\ |   \| __/ __| |_ _|_ _|_ _|
 | __ |/ _ \| |) | _|\__ \  | | | | | | 
 |_||_/_/ \_\___/|___|___/ |___|___|___|
                                                              
\n\n\n
"""
NYX_HEADER = """
|\ | \ / \_/ 
| \|  |  / \ 
"""
INTRO_TEXT = """
/   Melinoë, dearest, rumour has it you seek to go higher even.
|   Father has been glaring at me ever since your latest advents.
|   I do not think he would approve of such. It took time to convince
|   him otherwise. He has instructed me to come to you with this one 
|   final challenge. Were you to prove ready, he would aid you in
\   all that is to come. I believe in you. I love you.
"""
FAIL = """
...the light fades. Back to the forest you go.
"""
SUCCESS = """
Soul vanquished.
"""
WIN_TEXT = """
/   Splendid!
|   
|   I knew you could do it. Here, have this. You Father wanted you
\   to have it once you're ready.
"""
def main():
    souls = 20
    questions = 20
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
