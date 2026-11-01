#  Space Echoes

**Author** : Marko Gordic  
**Difficulty**: <font color='lightgreen'>Very Easy</font>  
**Description**: Amidst the silent void of the cosmos, a faint signal emerges, carrying secrets from an ancient civilization lost to time. You've stumbled upon coordinates encrypted with knowledge that predates the stars, a message beckoning from the edges of the unknown. Deciphering its contents could unravel the mysteries of the universe, or it could lead you down a path from which there is no return. The choice is yours: will you heed the call of the cosmos and unlock the secrets that lie beyond? 

## Solution

Inside the zip file, there is a file called `capture.pcapng`. This is a packet capture file. We can open it with Wireshark. User need to extract the file from the pcapng file. Inside the TCP stream, we can find plaintext part 1 and part 3 of the flag. Part 2 is base64 encoded. After decoding it, we can find the last part and get the full flag.
