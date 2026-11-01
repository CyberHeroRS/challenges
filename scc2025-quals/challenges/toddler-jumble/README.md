# PWN - Toddler Jumble
**Author** : k4  
**Difficulty** : <font color='orange'>Medium</font>
**Description** : Easiest heap chal.

Attachments:
+ pwn_toddler_jumble.zip

**Flag**: `SCC{even_a_baby_could_solve_this}`

# Writeup
Simply fill the tcache and perform the classic ABA fastbin double free.
See the exploit script and https://github.com/shellphish/how2heap/issues/200 .
