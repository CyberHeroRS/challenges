### Challenge description

The program encrypts a fixed-size flag using matrix multiplication: **Ax = b (mod n)**. The obfuscation is based on (s)printf's **%n** format specifier, which allows the function to write to memory.

The values of the matrix **A** and the modulus **n** can be recovered from the source code, while the vector **b** is given. 

It remains to solve the linear system to find the flag **x**, which is the unique solution.