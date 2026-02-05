# Notary [PWN]

Easy heap exploitation challenge with minimal checks. Upon free-ing a chunk of memory, a pointer writes itself on the content length variable for an easy overflow upon edit. At the same time, if the content length is large enough, you get the libc pointer to leak. After preparing the chunks you can overwrite one with the `__free_hook` address. Reallocate the chunk to set `system` to the hook and execute the shell by deleting a note. The details are in the comments of the solve script.

**FLAG: SCC{Th3r3S_n0_H34p_1ikE_a_n07es_h3aP}**
