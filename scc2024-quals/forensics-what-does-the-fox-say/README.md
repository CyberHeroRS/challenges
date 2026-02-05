# What Does The Fox Say?

**Author** : Marko Gordic  
**Difficulty** : <font color='orange'>Medium</font>  
**Description**: 
In the shadowy realms of cyberspace, where secrets lie hidden in the digital ether, your ally, the enigmatic CyberHero, has vanished without a trace. Tasked with unraveling the mystery of their disappearance, you must delve into the arcane depths of CyberHero's browser, a labyrinth of codes and clues. Within this digital Pandora's box, you will seek out the vestiges of their online journey, piecing together the puzzle to ensure their intentions were pure. Can you navigate this web of intrigue and uncover the truth behind CyberHero's activities before it's too late?  
**Flag**: `SCC{r1n9_d1n9_D1N9_D1N9_d1N93r1n93d1n!}`

## Challange

- Quesstionare, browser forensics

## Summary
1. What was the first website CyberHero visited? (e.g. Facebook, Pinterest, etc.) -> Reddit
2. What was the full URL for the first subreddit CyberHero visited? -> https://www.reddit.com/r/rust/
3. Is there any strange URL CyberHero visited while browsing? If yes, what is the URL? (format: https://website/) -> http://192.168.31.129/
4. What was the title of the strange URL CyberHero visited? -> CyberHero's Secret Vault
5. How many times did CyberHero visit the panel? -> 3
6. CyberHero wanted to buy tickets for a concert. What was the name of the band? -> Arctic Monkeys
7. When he searched for the band, what was the search term? -> arctic monkeys concert 2024
8. What are the credentials CyberHero used to log in to the secret panel? (format: username:password) -> admin:GSV1F9309uG6jDuCoTty9i5T2

## Solution

User is given a zip with Mozzila Firefox profile. Inside profile folder there are many artifacts that can be used to answer the questions. The most important artifacts are: `places.sqlite`, `formhistory.sqlite`, `cookies.sqlite`, `logins.json` and `webappsstore.sqlite`.

There is a online tool which can be used for easy password decryption : https://github.com/unode/firefox_decrypt

### 1. What was the first website CyberHero visited? (e.g. Facebook, Pinterest, etc.) -> Reddit
### 2. What was the full URL for the first subreddit CyberHero visited? -> https://www.reddit.com/r/rust/
### 3. Is there any strange URL CyberHero visited while browsing? If yes, what is the URL? (format: https://website/) -> http://192.168.31.129/
### 4. What was the title of the strange URL CyberHero visited? -> CyberHero's Secret Vault
### 5. How many times did CyberHero visit the panel? -> 3
### 6. CyberHero wanted to buy tickets for a concert. What was the name of the band? -> Arctic Monkeys

We can use `places.sqlite` to find solutions to all of these.

###  7. When he searched for the band, what was the search term? -> arctic monkeys concert 2024

We can use `formhistory.sqlite` to find the search term.

### 8. What are the credentials CyberHero used to log in to the secret panel? (format: username:password) -> admin:GSV1F9309uG6jDuCoTty9i5T2

We can use tool mentioned above to decrypt the password, and find the username.