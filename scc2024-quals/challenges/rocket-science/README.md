#  Rocket Science

**Author** : Mihajlo Krsmanovic  
**Difficulty**: <font color='red'>Hard</font>  
**Description**:  CyberHero has just optimized their network with a cutting-edge internet acceleration program. However, amidst the boost in cyber speed, a critical file has mysteriously disappeared. Can you delve into the digital depths and retrieve the lost asset before it's too late?

Flag: ``SCC{c2_5ur3_5p33ds_up_w1nd0w5}``


## Solution

From memdump we can find speedrocket.dll which is the c2 client. Opening it in dnSpy we can analyze how it works.

In pcap we can find AES password parts, combining it we get `cyberhero7b3b8f6`.

Scrolling through the packets, we find one with big payload, which is encrypted pdf file which was missing.

Decrypting it with SpeedCrypt, we get base64 encoded pdf, decode it and get base64 encoded flag.


