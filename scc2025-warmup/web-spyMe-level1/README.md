## Ime zadatka:

SpyMe Level 1


## Kategorija:

Web

## Deskripcija:

> A secret espionage operation is unfolding in the Balkans, aiming to influence regional governments. We've gained access to their internal platform. Can you infiltrate their system and retrieve information from the spies' accounts?


## Linkovi:

+ `source.zip` - [Download](https://github.com/CyberHeroRS/scc2025-warmup/raw/refs/heads/master/web_spyMe_level1/public/source.zip)

## Flag:

* `SCC{th0s3_g0dd4Mn_S3rbS!}`

## Napomene:

* Zameniti fake flagove unutar `docker-compose.yml` fajla.
* Staviti neke jace credentials za MySQL takodje unutar `docker-compose.yml` fajla.
* Koristiti istu instancu za sva 3 level-a zadatka.

## Writeup:

* IDOR unutar `/api/account_info/` endpoint-a.
* Uzima base64-encoded JSON - npr `{"id": 1}`
* Jednostavno inkrementnom pretragom preko svakog ID-a dobijamo `secretCode` od nekog od agenata.
* Nakon logina, dobijamo flag.
* Exploit unutar `checker/solve.py` fajla.


