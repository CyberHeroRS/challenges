#  Ghostwriter Mystery

**Author** : Mihajlo Krsmanovic  
**Difficulty**: <font color='green'>Easy</font>  
**Description**:  In the dimly lit corners of the digital realm, a specter of the past has left whispers in the wind. "Ghostwriter Mystery" beckons CyberHero to unveil secrets encrypted within the silent dance of keys. Dare to decipher the ghostly script, and unearth truths buried beneath the echoes of a forgotten stroke.

## Solution

[CTF USB keyboard parser](https://github.com/carlospolop-forks/ctf-usb-keyboard-parser) can be used to solve the challenge easily - the only difference is looking for ⌫ instead of \[BACKSPACE\].

The following command extracts needed data to text file:
```
tshark -r ghostwriter.pcap -Y '(usb.src == "1.16.1")' -T fields -e usbhid.data | sed 's/../:&/g2' > commands.txt
```

After that run the modified script:
```
python keyboard.py commands.txt
```

The script returns the flag: `SCC{3cho35_0f_7h3_51l3nt_9h057wr173r}`
