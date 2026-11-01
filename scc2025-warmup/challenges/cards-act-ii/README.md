# CRY - Cards, Act II

**Author** : Lofer
**Difficulty**: Medium
**Description**: Another card game to decide your life. Maybe you should start avoiding dimly lit rooms...

**External resources**:
- `cards.py` - [Download](public/cards.py)

**Flag**: ``SCC{subroups_are_groups_too}``

## Napomene

Remote zadatak. Dockerfile nije u ``/public``, idk jel mora biti.

# Writeup

Generate a prime $p$ such that its order (i.e. $p-1$) is divisible by a small integer larger than two (ex. 3). Once done so, we can submit $p$ as our prime, and for a multiplicative generator $g$, we can submit $g^{\frac{(p-1)}{3}}$ as our generator. This results in a small subgroup that we can abuse. By guessing what value the state will have mod 3, we can predict the cards.