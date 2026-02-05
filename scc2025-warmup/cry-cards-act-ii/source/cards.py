import random
from Crypto.Util.number import isPrime
SUITS = ["♠", "♥", "♦", "♣"]

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
    
    def from_value(val):
        suit = val // 13
        value = (val % 13) + 1
        return Card(value, SUITS[suit])

class NextGenRandom:
    def __init__(self, g, p):
        self.g = g
        self.p = p
        self.state = random.randint(0, p)
    
    def next_card(self):
        self.state = pow(self.g, self.state, self.p)
        return Card.from_value(self.state % 52)

def game_over():
    print("It seems this has been a waste of my time, again.\n")
    print("*You are shot from behind, dying instantly.*")
    exit()

if __name__ == "__main__":
    print("*You sit at a small round table. It looks familiar. The lights dim.\nAt the opposite side of the table sits a hooded man with a deck of cards.\nThe deck looks unusually large.*")
    print("\n- Let's see if you are worthy.\n")

    print("First, the conditions: I choose the seed. You choose the rest.")
    print("p (hex): ", end="")
    p = int(input(), 16)
    if not (isPrime(p) and p > 2**256):
        print("No cheating.")
        exit()
    print()
    print("g (hex): ", end="")
    g = int(input(), 16)
    if not (2 < g < p-1):
        print("No cheating.")
        exit()
    print()
    
    ngr = NextGenRandom(g, p)
    current_card = Card(5, SUITS[0])
    for round in range(50):
        print("Larger? [y/n] - ", end="")
        commit = input().strip().lower() == 'y'
        print()
        new_card = ngr.next_card()
        if commit:
            if new_card.value > current_card.value:
                continue
            else:
                game_over()
        else:
            if new_card.value < current_card.value:
                continue
            else:
                game_over()
    
    print("Bravo. Not that disappointing after all. Here, take this:")

    import os
    flag = os.getenv("FLAG", "SCC{fake_flag}")
    print(flag)
