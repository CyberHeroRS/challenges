# VMderful

**Author**: Jovan Pavlovic
**Difficulty**: <font color='lightgreen'>Medium</font>  
**Description**: I made my new website using cool new technologies. I hope its safely secured on cloud.
**Infrastructure requirements**: zip  

Flag: `SCC{w45M_i5NT_Th4t_H4RD_0r_I5_It?}`

# Solution

Using browser check sources tab, and open wasm file.
Figure out there is check_flag function and see that it uses RC4 encryption on input with hardcoded key and expected result.
