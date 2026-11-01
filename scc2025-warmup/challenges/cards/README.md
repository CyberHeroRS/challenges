# PWN - Cards
**Author** : k4  
**Difficulty** : <font color='green'>Easy</font>  
**Description** : Do you feel lucky, punk?  

Attachments:
+ pwn_cards.zip - [Download](https://example.org/)

**Flag**: `SCC{luck_is_not_the_only_f4ctor}`

# Writeup
### Overview
The challenge let's us play a simple game of guessing whether the drawn card
is higher or lower than the last drawn card.
```
*You sit at a small round table. The lights dim.
At the opposite side of the table sits a hooded man with a deck of cards.
The deck looks unusually large.*

- Let's see if you are worthy.

*He shuffles the deck and hands you a card: there is no suite, it only says "5".*

- Higher, or lower?

+ [h/l]: h

*He draws another card, looks at it, and places it face down.*

- Correct.

*He sets the card aside*

- Higher, or lower?

+ [h/l]: l

*He draws another card, looks at it, and places it face down.*

- It seems this has been a waste of my time.

	*You are shot from behind, dying instantly.*
```
There is some vagueness on what the game is exactly, so the binary needs to be reversed a bit.
Some relevant bits are.

![image](https://github.com/user-attachments/assets/8d296e9a-7dff-4e82-97ce-2a3b214fd4e7)

Our card is always updated.

![image](https://github.com/user-attachments/assets/4d2e0dd3-8e5b-48d0-8cb8-72872693d2bb)

The new card will never have the same value as the current card.

![image](https://github.com/user-attachments/assets/4c588d41-4817-4934-b551-25db5ea5f1dc)

There are 200 rounds.

![image](https://github.com/user-attachments/assets/e5e93c55-d5a8-4302-bb0b-921ccbd5f70f)
![image](https://github.com/user-attachments/assets/dc46c2b8-3d8d-4312-a891-71da56923a49)


If we win the game, we get the flag.

### The Vulnerability
![image](https://github.com/user-attachments/assets/93447df3-e9de-41df-badf-9c3a952b2a0b)

The issue is quite simple, the complete state of the random number generator is determined
by `time(NULL);`, which is something we can predict. Thus, if we just replicate the logic
of the code in our exploit, we can predict the value of every card that will be drawn and
play accordingly. This gives us our exploit:
```python
from ctypes import CDLL

def draw_card():
    return (libc_call.rand() % (13 - 1 + 1)) + 1;

libc_call = CDLL("/usr/lib/libc.so.6")

p = start()

# Hopefully we get the same unix time
# here, as will the remote server.
libc_call.srand(libc_call.time(0))

cur_card = 5

for i in range(200):
    next_card = draw_card()
    while next_card == cur_card:
        next_card = draw_card()

    c = b'h' if next_card > cur_card else b'l'
    p.sendlineafter(b'[h/l]: ', c)
    cur_card = next_card

p.interactive()
p.close()
```
![image](https://github.com/user-attachments/assets/0bdba94f-8cba-4572-abf0-f83dbaf9d0a7)

GG :>
