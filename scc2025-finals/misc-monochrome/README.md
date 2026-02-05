# Monochrome [MISC]

Network traffic challenge with USB traffic from a keyboard and a Wacom graphical tablet. You need to parse the HID data from both devices. Parsing the keyboard traffic reveals a hint explaining how the challenge was created. Parsing the Wacom traffic allows reconstruction of a QR code, which contains the flag. Solve scripts are available in the repository.

**FLAG: SCC{HIDHIDHURA}**