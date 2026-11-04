# Entropy u podrumu

Kada je Nikola prvi put sišao u podrum stare zgrade Tehničkog fakulteta,
mislio je da traži samo izgubljeni patch kabl. Umesto toga, pronašao je
nešto mnogo opasnije --- server koji nije postojao ni u jednom
inventaru.

Podrum je mirisao na vlagu i prašinu. Rack orman je stajao u ćošku,
povezan jednim tankim UTP kablom koji je nestajao kroz zid. Nije bilo
oznaka, nije bilo asset taga, nije bilo nalepnica. Samo mali crveni LED
koji je pulsirao u pravilnim intervalima, kao da diše.

Nikola je bio poznat po tome što je učestvovao na svakom CTF-u koji je
mogao da pronađe. Reverse engineering, binary exploitation,
kriptoanaliza --- sve mu je to bilo bliže od prosečnog razgovora sa
ljudima. Kada je video nepoznati server, instinkt mu nije rekao da
pozove administratora. Rekao mu je: enumeracija prvo.

Povezao je laptop direktno na kabl i podesio statičku IP adresu.\
`nmap -sS -sV -p- 10.13.37.1`

Portovi su počeli da se pojavljuju.

22/tcp open ssh\
80/tcp open http\
31337/tcp open unknown

Na web servisu bila je jednostavna stranica, crna pozadina i zelena
monospaced slova:

> Dobrodosao, istrazivacu. Ako ovo citas, znaci da si vec probio fizicki
> perimetar. Sada sledi digitalni.

U HTML komentaru krio se Base64 string. Nakon dekodiranja dobio je
poruku:

`TrustNoOneButTheEntropy`

Port 31337 je tražio proof-of-work. SHA256 hash sa pet vodećih nula.\
Nikola je napisao mali brute-force skript. Posle nekoliko minuta server
je prihvatio odgovor i poslao binarni fajl.

Otvorio ga je u Ghidra-i.

Main funkcija je bila očigledno obfuskovana. Anti-debug check preko
ptrace, zatim XOR-ovana sekcija sa runtime dekripcijom. Nikola je
patchovao proveru i pustio program kroz debugger.

Program je tražio unos od 32 bajta.

Kada bi uneo pogrešan string, dobijao je poruku:

> Integrity compromised.

Nikola je analizirao funkciju validacije. Koristila je kombinaciju
CRC32, SHA1 i custom rotacionu operaciju sličnu ARX konstrukcijama.
Podsetilo ga je na pojednostavljeni dizajn blok-šifre.

Na sredini koda primetio je interesantan string koji nije bio
referenciran direktno:

SCC{f4k3_fl4g_f0r_73s7ing}

Nasmejao se. Previše očigledno.

Ali string nije bio u plain-textu u memoriji tokom izvršavanja. Bio je
fragmentisan u četiri dela, svaki dodatno XOR-ovan sa različitim ključem
izvedenim iz vremena pokretanja procesa.

"Znači, time-based key derivation", rekao je.

Server je očigledno generisao ključ koristeći `time(NULL)` podeljen sa
60, zaokružen na minut. To je značilo da flag može biti rekonstruisan
samo u određenom vremenskom prozoru.

Nikola je napisao skript koji brute-force-uje vremenski opseg poslednjih
24 sata i pokušava sve moguće minute kao seed. Posle nekoliko iteracija,
jedan izlaz je izgledao smisleno.

Program je prihvatio unos.

Na ekranu se pojavila nova poruka:

> Dobrodosao u drugi sloj.

SSH servis je sada prihvatao login sa kredencijalima koje je dobio kao
rezultat prve faze. Nakon prijave, našao se u minimalnom Linux okruženju
bez većine standardnih alata.

`ls` je bio alias na skriptu koja filtrira izlaz. `cat` je bio wrapper
koji zabranjuje pristup određenim fajlovima. PATH je bio modifikovan.

"Restricted shell", pomislio je.

Pronašao je SUID binarni fajl u /usr/local/bin. Binarni fajl je bio
vlasništvo root-a i imao je execute dozvole.

Brza analiza sa `strings` pokazala je poziv na `system()` funkciju bez
sanitizacije unosa.

Klasična command injection prilika.

Nikola je pažljivo konstruisao payload koristeći backtick sintaksu i
uspeo da dobije interaktivni root shell.

U /root direktorijumu nalazio se samo jedan fajl: `entropy.log`.

Fajl je sadržao niz hash vrednosti i vremenskih oznaka. Svaka linija je
imala format:

timestamp \| sha256 \| status

Status je bio ili OK ili FAIL.

Poslednja linija je glasila:

> 1700000000 \| e3b0c44298fc1c149afbf4c8996fb924... \| OK

Hash je bio SHA256 praznog stringa.

"Znači validacija nulte poruke", zaključio je.

Na kraju fajla, u heksadecimalnom dump-u, nalazila se skrivena poruka
kodirana kao ASCII u heks formatu. Dekodiranjem je dobio:

> Entropy is the only truth. Everything else is assumption.

Ispod toga, konačno, kompletan flag u čistom tekstu:

SCC{fr3qu3nci3s_4r3_high_wi7h_7his_0n3}

Nikola je zastao.

Ovo nije bio običan CTF zadatak. Ovo je bio test. Test razumevanja
sistema, test strpljenja, test sposobnosti da poveže fizički i digitalni
svet.

Server u podrumu nije bio samo mašina. Bio je metafora. Bez inventara,
bez dokumentacije, bez nadzora --- kao mnogi sistemi u stvarnom svetu.

Shvatio je da prava poenta nije samo pronalaženje flag-a. Poenta je bila
u procesu: enumeracija, analiza, eksploatacija, eskalacija privilegija,
forenzika.

U trenutku kada je zatvorio laptop, LED na serveru je prestao da
pulsira.

Kada je sledećeg dana pokušao ponovo da se poveže, server više nije
odgovarao. Kao da nikada nije ni postojao.

U podrumu je ostao samo prazan rack.

Nikola je znao da će neko drugi jednog dana pronaći sledeći sloj.

Jer u svetu bezbednosti, svaki sistem je samo privremeno siguran.

A entropija uvek pobeđuje.
