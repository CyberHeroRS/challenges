# Neglegentia

**Author** : Dušan Lazić

**Difficulty** : Easy

**Description** : Our most skilled social engineer managed to access notorious hackers' private network (he stole their WPA2 password), register his own account on their custom chat platform and steal the source code. Since you are our most skilled hacker, he gave you the credentials (`johmdoe:password123`) and the source code. Your mission is to get our flag back. Those chats may be hiding something ...

**Flag** : `SCC{r3m3mb3r_t0_v3r1fy_uR_JWT}`

# Solution

The solution involves recognizing that the `jwt.decode()` method is used rather than `jwt.verify()`, resulting in broken authentication vulnerability. An SQL injection vulnerability in the `sub` field of the JWT token allows account takeover, which makes possible to access and read through the chats of other users. The flag is stored in plaintext in one conversation that shouldn't be too hard to find.
