# CRY - Gods & Monsters

**Author** : Lofer
**Difficulty**: <font color='red'>Hard</font>  
**Description**: You stand atop the summit, a trail of bodies lay behind you. You brace yourself. "This is it", you utter, and the doors open to reveal a creature beyond comprehension. Slay it, and you shall go down in history.

**External resources**:
- `gods_and_monsters.py` - [Download](public/gods_and_monsters.py)
- `out.txt` - [Download](public/out.txt)

**Flag**: ``SCC{ev3n_g0d5_bl33d}``

# Writeup

Realise the script is just using explicit point addition formulae. Using a website like [this](https://crypto.stanford.edu/pbc/notes/elliptic/explicit.html) translate the magic numbers into a curve. Using SageMath, factor the order of the generator. Realise it's relatively smooth. Run a Pohllig-Hellman variant, retrieve 64 bits, brute remaining 5 or so bits.

Sample SageMath solution:
```py
EC = ...
# Elliptic Curve defined by y^2 + x*y + 36705335186416557299559736926700113135726096437924011941539879171053079785019*y = x^3 + 27723118983053438240314554566919304702009372842675523657054796985533101035967*x^2 + 13135011342158767390972930743879758669664065038225826254653566661198441680369*x + 45493736686359268253421923085820265975471414362134679444217955415112786078568 over Finite Field of size 67971422875209843218823497319855231593203446798693404917904261220233138364877
G = ...
P = ...

o = G.order()
mods, rems = [], []
for facTuple in o.factor()[:-1]:
    t = facTuple[0]^facTuple[1]
    v = o // t
    r = (G*v).discrete_log(P*v)
    mods.append(t)
    rems.append(r)

a, b = o.factor()[:-1]
a = a^b
n_ = crt(rems, mods)
while n_ * G != P:
    n_ += o // a
print(n_)
```