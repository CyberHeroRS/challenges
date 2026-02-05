# The Three-Encryption Problem

**Author** : Lofer  
**Difficulty** : Medium  
**Description**: 
Maybe Cixin had the right idea. Three is such a perfect number... can you prove me right?

**Flag**: `SCC{thr33_is_th3_b3st_numb3r!?_D1D_U_br4t3_@l1_0f_th1$?!?_I_hpe_nO!t_:)}`

## Solution

Use knowledge of flag prefix to retrieve `p`, `q`, and `n`. Can simply be done by factoring the message / brute-forcing combinations. Then brute force triplets to decrypt the rest of the flag.