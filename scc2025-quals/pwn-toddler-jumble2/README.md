# PWN - Toddler Jumble 2
**Author** : k4  
**Difficulty** : <font color='red'>Hard</font>
**Description** : Literarly the same chal

Attachments:
+ pwn_toddler_jumble2.zip

**Flag**: `SCC{when_you_were_little_you_played_with_chunks_instead_of_legos}`

# Writeup
The trick is to cause the fastbin chunks to consolidate by allocating a large chunk (see where malloc_consolidate is called in glibc/malloc/malloc.c). Now, although the program doesn't let us allocate such a chunk, we can cause libc to do so by passing a large input to scanf. After fastbin chunks are consolidated we can easily get an overlapping chunks primitive and perform tcache posion. See checker/exploit.py for more details.
