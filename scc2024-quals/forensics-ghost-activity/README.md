#  Ghost Activity

**Author** : Mihajlo Krsmanovic  
**Difficulty**: <font color='orange'>Medium</font>  
**Description**:  CyberHero returned from his journey to find echoes in his digital domain, suggesting an uninvited guest had been at his computer. He sent you the memory dump, a cryptic puzzle of activity and silence, for analysis. Your mission: sift through the shadows, decode the mystery, and reveal the intruder's digital dance.

## Solution

After connecting to server with netcat, player will be faced with 7 questions that are all solved with volatility:

1. What are major and minor version of Windows? (\<major\>.\<minor\> eg 5.2)
=> 10.0
```
python vol.py memdump.mem windows.info => PE MajorOperatingSystemVersion  10, PE MinorOperatingSystemVersion  0 
```
2. What is the username of the current user? 
=> cyberhero
```
python vol.py memdump.mem windows.envars
```
3. What is the nthash of cyberhero? 
=> f8f880509d176c4c4c23c8e55d0da5dc
```
python vol.py memdump.mem windows.hashdump
```
4. CyberHero was preparing an email for his friend using popular text editor, what is its pid? 
=> 9096
```
python vol.py memdump.mem windows.pstree
```
5. In the email, CyberHero mentioned marathon. What was friend's name? 
=> Royce
```
python vol.py memdump.mem windows.memmap --dump --pid 9096 => strings => search for marathon
```
or get notepad plugin at https://github.com/spitfirerxf/vol3-plugins

```
python vol.py windows.notepad => search for marathon
```
6. CyberHero was testing his download speed by trying to download large file using a srcipt language, can you find URL that he was targeting? 
=> https://hil-speed.hetzner.com/1GB.bin
```
python vol.py memdump.mem windows.envars 
```
7. At which time was connection to that site established? (yyyy-mm-dd hh:mm:ss) 
=> 2024-03-17 13:02:35
```
python vol.py memdump.mem windows.netscan 
or
pyhton vol.py memdump.mem windows.netstat
```
