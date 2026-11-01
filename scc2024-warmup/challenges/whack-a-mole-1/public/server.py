from Crypto.Util.number import *
import random

# nije deo zadatka, samo crtezi krtica
krtica_banner="\n\n["+" "*21+"/===\\"+" "*29+"]\n["+" "*20+"/o  o \\"+" "*28+"]\n["+" "*19+"/ ----  \\"+" "*27+"]\n[     _____ ...     ---------   _____   _____ ... _____ ]\n\n"
win_banner="[  TACNO!!"+" "*14+",\n["+" "*22+"/(  ___________\n["+" "*21+"|  >:===========`\n["+" "*22+")(\n["+" "*22+"\"\"\n["+" "*20+"/===\\"+" "*29+"]\n["+" "*19+"/x  x \\"+" "*28+"]\n["+" "*18+"/   o   \\"+" "*27+"]\n[    _____ ...     ---------   _____   _____ ... _____ ]\n"
fail_banner="[  NETACNO :p"+" "*11+"\n["+" "*40+",\n["+" "*21+"/===\\"+" "*13+"/(  __________  ]\n["+" "*20+"/ ^  ^\\"+" "*11+"|  >:==========1 ]\n["+" "*19+"/    U  \           )("+" "*14+"]\n[     _____ ...     ---------   _____   \"\" ... _____    ]\n"

# broj koji dobijete za seed, posaljite kao drugu zastavicu u obliku "flag{VREDNOST_SEED_BROJA}"
# ako zelite da testirate skriptu lokalno, zamenite string "<IZUZETO>" sa brojem od 24 cifre, na primer:
# seed=111111111111111111111111
seed="<SAKRIVENO>"
seed=111111111111111111111111

# klasa koja implementira osnovni oblik LCG-a
class LCG() : 
    def __init__(self,seed) : 
        self.seed = seed
        self.a = getPrime(self.seed.bit_length())
        self.c = getPrime(self.seed.bit_length())
        self.m = getPrime(self.seed.bit_length() + 1)
    def next(self) : 
        self.seed = ((self.seed * self.a) + self.c) % self.m
        return self.seed

# glavni deo zadatka
l = LCG(seed)
s1=l.next()
s2=l.next()
s3=l.next()

# glavni meni
print("  [-] Dobro dosli u poznatu igru na vasarima, \"istrebite krtice iz dvorista\"")
print(f"     U dvoristu postoji {l.m} rupa, koje su napravile 5 krtica")
print("     Dajte sve od sebe da pobedite svih 5 krtica!")
print(krtica_banner)

# podaci neophodni takmicaru
print("\nizracunata stanja:", s1, s2, s3)

# proveravanje korisnickog inputa
for i in range(5):
    s4=l.next()
    print(f"Koji broj rupe zelite da udarite cekicem? (0 - {l.m})")
    usr=input()
    if(int(usr) == s4): print(win_banner)
    else: 
        print(fail_banner)
        quit()

# ovde ce biti prikazana druga zastava, kada uspesno predvidite pozicije sledecih 5 krtica
print("ZASTAVA: flag{<SAKRIVENO>}")
