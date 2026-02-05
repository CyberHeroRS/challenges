import Crypto.Random as rand
import Crypto.Hash.SHA1 as sha1
import base64
import time 
import os

from colorama import Fore, Back, Style, Cursor
from colorama import ansi, init

BANNER = Fore.GREEN + """
 /$$$$$$$  /$$                 /$$                   /$$              /$$                                   
| $$__  $$|__/                | $$                  | $$             | $/                                   
| $$  \\ $$ /$$  /$$$$$$       | $$$$$$$   /$$$$$$  /$$$$$$   /$$$$$$$|_/                                    
| $$$$$$$ | $$ /$$__  $$      | $$__  $$ /$$__  $$|_  $$_/  /$$_____/                                       
| $$__  $$| $$| $$  \\ $$      | $$  \\ $$| $$$$$$$$  | $$   |  $$$$$$                                        
| $$  \\ $$| $$| $$  | $$      | $$  | $$| $$_____/  | $$ /$$\\____  $$                                       
| $$$$$$$/| $$|  $$$$$$$      | $$$$$$$/|  $$$$$$$  |  $$$$//$$$$$$$/                                       
|_______/ |__/ \\____  $$      |_______/  \\_______/   \\___/ |_______/                                        
               /$$  \\ $$                                                                                    
              |  $$$$$$/                                                                                    
               \\______/                                                                                     
  /$$$$$$            /$$ /$$                            /$$$$$$                      /$$                    
 /$$__  $$          | $$|__/                           /$$__  $$                    |__/                    
| $$  \\ $$ /$$$$$$$ | $$ /$$ /$$$$$$$   /$$$$$$       | $$  \\__/  /$$$$$$   /$$$$$$$ /$$ /$$$$$$$   /$$$$$$ 
| $$  | $$| $$__  $$| $$| $$| $$__  $$ /$$__  $$      | $$       |____  $$ /$$_____/| $$| $$__  $$ /$$__  $$
| $$  | $$| $$  \\ $$| $$| $$| $$  \\ $$| $$$$$$$$      | $$        /$$$$$$$|  $$$$$$ | $$| $$  \\ $$| $$  \\ $$
| $$  | $$| $$  | $$| $$| $$| $$  | $$| $$_____/      | $$    $$ /$$__  $$ \\____  $$| $$| $$  | $$| $$  | $$
|  $$$$$$/| $$  | $$| $$| $$| $$  | $$|  $$$$$$$      |  $$$$$$/|  $$$$$$$ /$$$$$$$/| $$| $$  | $$|  $$$$$$/
 \\______/ |__/  |__/|__/|__/|__/  |__/ \\_______/       \\______/  \\_______/|_______/ |__/|__/  |__/ \\______/ 
                                                                                                            
                                                                                                            
                                                                                                            
""" + Style.RESET_ALL

TOAST = Style.DIM + f":>  The only casino where you can {Style.BRIGHT}only{Style.DIM} bet big{Style.RESET_ALL}"

WELCOME = "Welcome new player, you are extra lucky today and have won 1.00$"

MENU="""
Choose an action:
    1.) Play Real Horse Racing
    2.) Simulate Horse Racing
    3.) Buy more currency
    4.) Provably Fair
    5.) Shop
"""

PF_MENU="""
Choose an action:
    0.) Exit menu
    1.) Set client seed
"""

PF_HELP_TEXT = """ 
Provably fair is a way for you to verify that games played here are truly
random. Games played here are generated using both a client seed and
server seed.

1. The sha256 hash of the server seed is sent to the player (sha1.new(serverSeed).hexdigest())
    Currently: {}
2. The player can modify thier client seed
    Currently: {}
3. The player starts the game
4. The server takes the server seed and client seed and combines them as such: (serverSeed + bytes.fromHex(clientSeed))
5. The server then uses the sha1 digest of the combined seed as the seed for the game (sha1.new(combinedSeed).digest())
6. The game finishes
7. The server reveals its server seed
8. A new server seed is generated

"""

SHOP="""
    Purchase Items:
    ID | NAME      | PRICE
    ------------------------------------------
    1. | Flag           | 65536.00$
    2. | Popping Gadget | 256.00$
    3. | Nothing?       | 4.00$
    4. | Skidd Pass     | 1.00$
"""

ITEMS=[
    os.getenv("FLAG", "SCC{REDACTED}"),
    "What's a pop gadget... 3. 2. 1. SKIIIIIID!!!",
    "Congragulations?",
    "Here is the flag SBB{Y0u_4r3_know_skid!}"
]

PRICES=[65536, 256, 4, 0]

HORSE_TRACK = """| 1 | 2 | 3 | 4 |
|___|___|___|___|____ START 
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|   |   |   |   |
|___|___|___|___|____ END 
|   |   |   |   |
"""

def animate_horse_race(seed : bytes, real = False) -> int:
    import random
    cursor = ansi.AnsiCursor()
    print('\033[?25l', end="")
    print(ansi.clear_screen() + cursor.POS(), end='')
    print(HORSE_TRACK)
    Horses = [1,1,1,1]
    HorsesC = (Fore.GREEN,Fore.RED,Fore.YELLOW,Fore.BLUE)
    HorsesX = (3,7,11,15)
    for i in range(4):
        print(cursor.POS(HorsesX[i], Horses[i]+1) + HorsesC[i] + "H" + Style.RESET_ALL, end="", flush=True)
    rng = random.Random(seed)
    while not 14 in Horses:
        h = rng.randint(0,3)  
        print(cursor.POS(HorsesX[h], Horses[h]+1) + " " + cursor.DOWN() + cursor.BACK() + HorsesC[h] + "H" + Style.RESET_ALL, end="", flush=True)
        Horses[h] += 1
        time.sleep(0.1)
    time.sleep(1)
    print(cursor.POS(20,6)+f"Horse {Horses.index(14)+1} won the race!!", end="", flush=True)
    if(real): 
        print(cursor.POS(20,7)+f"The seed was: {ServerSeed.hex()}")
    print(cursor.POS(1,18))
    print('\033[?25h', end="")
    return Horses.index(14)

def RealBet():
    global balance
    global ServerSeed
    
    if(balance <= 0):
        input("Contact the admins for a bitcoin wallet for adding funds to")
        return
    

    try:
        bet = int(input("What horse to put it all on? [1-4] "))-1
        if not bet in range(4):
            return
    except (TypeError,ValueError):
        return
    
    winner = animate_horse_race(sha1.new(ServerSeed+ClientSeed).digest(),True)
    if(winner == bet):
        balance *= 2
        print(f"You win!!! New balance: {balance}.00$")
    else:
        balance = 0
        print("Womp-womp looks like you can join the loosers table")
    ServerSeed = rand.get_random_bytes(16)
    print(f"New PF Hash is: {sha1.new(ServerSeed).hexdigest()}")
    
def FakeBet():
    seed = b""
    try:
        seed = bytes.fromhex(input("enter seed: "))
    except:
        pass
    if(seed == b""):
        seed = rand.get_random_bytes(16)
    animate_horse_race(seed)

def PF():
    global ClientSeed
    print(ansi.clear_screen() + Cursor.POS() + PF_HELP_TEXT.format(sha1.new(ServerSeed).hexdigest(), ClientSeed.hex()) + "\n\n")
    print(PF_MENU + "\n")
    opt = input(":? ")
    match opt:
        case "1":
            try:
                ClientSeed = bytes.fromhex(input("Enter ClientSeed (hexencoded): "))
            except:
                return
        case default:
            return
    ClientSeed = rand.get_random_bytes(16) if (ClientSeed == b'') else ClientSeed

def Shop():
    global balance
    print(ansi.clear_screen() + Cursor.POS() + SHOP+"\n\n")
    try:
        i = int(input())-1
    except ValueError:
        return
    if not i in range(4):
        return
    
    if balance < PRICES[i]:
        print("Not enought moneyz for item")
        return
    
    balance -= PRICES[i]

    print(ITEMS[i])
    


balance = 1
ServerSeed = rand.get_random_bytes(16)
ClientSeed = rand.get_random_bytes(16)


try:
    if __name__ == "__main__":
        init()
        for c in BANNER:
            print(c, end='')
            time.sleep(0.0001)
        print(TOAST + "\n\n")
        print(WELCOME + "\n\n")
        while(1):
            print(MENU + "\n\n")
            print(f"Current balance: {balance}.00$\n")
            opt = input(":? ")
            match opt:
                case "1":
                    RealBet()
                case "2":
                    FakeBet()
                case "3":
                    print("Please purchase and send a 100$ steam giftcard to @Pimpest on discord, he will then make sure 100.00$ get added to your Big Bets' wallet")
                case "4":
                    PF()
                case "5":
                    Shop()
                case default:
                    pass
            x = input("\nPress enter to continue... ")
            print(ansi.clear_screen() + Cursor.POS() + "\n",end="")
except:
    print(Style.RESET_ALL)