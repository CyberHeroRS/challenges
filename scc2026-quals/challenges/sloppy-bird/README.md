## Ime zadatka:

Sloppy Bird

## Kategorija:

Rev

## Deskripcija:

> This is my first vibe-coded game. I hope you all like it and that it earns me a lot of money. 
> Players who reach a score of 274432 will receive a special reward, but please don't try to cheat or you will be banned.

## Flag:

* `SCC{1'm_s0m3_kind_0f_4_ch347ing_sl0pp3r_mys3lf!}`

## Napomene:

* *Game Hacking*

## Writeup:

Analizom same igrice i uz pomoć deskripcije lako je zaključiti da je potrebno nekako povećati *score* do velikog broja. Poznat alat koji služi ovoj svrsi jeste *Cheat Engine*.  

Prvo je potrebno ostvariti neki *score* u igri i pretražiti tu vrednost u *Cheat Engine*. Pretraga se vrši unosom vrednosti i likom na dugme *First Scan* koje nakon toga postaje *New Scan*.
![Image 01](./screenshots/img01.png)

Kako je dobijeno mnogo rezultata potrebno je nastaviti igru i ponovo pretražiti novi *score* i nakon toga ostaje samo jedna adresa na kojoj je najverovatnije sačuvana vrednost *score*-a. Pretraga nove vrednosti se vrši unosom vrednosti i klikom na dugme *Next Scan*.
![Image 02](./screenshots/img02.png)

Kada sačuvamo tu vrednost dvoklikom u polju za rezultate pretrage, dvoklikom na *Value* polje u sačuvanoj adresi možemo postaviti novu vrednost na neki veliki broj.
![Image 03](./screenshots/img03.png)

Promenom vrednosti pojavljuje nam se poruka da smo banovani jer smo pokušali da varamo u igri, ovo ukazuje na postojanje nekog *Anti-Cheat* sistema unutar same igre, ali kako je reč o *single-player* lokalnoj igri, ovo ne bi trebalo da predstavlja neki problem.
![Image 04](./screenshots/img04.png)

Otvaranjem igrice u nekom alatu za *Reverse Engineering*, pri korak kojim možemo krenuti jeste pretraga stringova. Pronalaskom stringova `CHEATER CHEATER` i `.banned` možemo pretpostaviti da je to nekako povezano sa stringovima između koji ukazuju na `HOME` direktorijum.
![Image 05](./screenshots/img05.png)

Ukoliko pogledamo u `HOME` direktorijumu trenutnog korisnika, vidimo da je kreiran fajl `.banned`, njegovim brisanjem i ponovnim pokretanjem igre vidimo da 'ban' više nije tu. Ponavljamo isti postupak kao na početku, ali sada analiziramo memoriju oko same *score* vrednosti. Vidimo da se odmah nakon nje čuva vrednost koja je za 1 manja od trenutne vrednosti.
![Image 06](./screenshots/img06.png)

Kako bi se uverili u pretpostavku da je vrednost nakon trenutno vrednosti prestavlja prethodnu vrednost, nastavimo sa igrom kako bi dobili još jedan poen, kako se oba *score*-a povećaju za 1, pretpostavka je tačna.
![Image 07](./screenshots/img07.png)

Čuvanjem adrese i promenom tipa na 8 *bytes*, dobijamo mogućnost da istovremeno promenimo obe vrednosti, to se može uraditi promenom jednog bita u višem delu *hex* zapisa broja.
![Image 08](./screenshots/img08.png)

Klikom na dugme za čuvanje adrese ažurira se *score*, ali ovaj put nismo banovani, već nam se pojavio *flag* koji predstavlja našu nagradu.
![Image 09](./screenshots/img09.png)