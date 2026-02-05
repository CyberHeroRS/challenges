#!/usr/bin/python
import os
import matplotlib.pyplot as plt

os.system("""tshark -r capture.pcapng -T fields -e usbhid.data -Y usbhid.data | sed 's/../:&/g2' > wacom.txt""")

x_values = []
y_values = []

x_values_white = []
y_values_white = []

change_colour = False
in_switch_zone = False

for line in open('wacom.txt').readlines():
    xyz = line.strip().split(":")
    if len(xyz) < 10:
        continue

    x = int(xyz[3] + xyz[2], 16)
    y = int(xyz[6] + xyz[5], 16)
    z = int(xyz[9] + xyz[8], 16)

    if z > 0:
        if x > 4000 and y < 2000:
            if not in_switch_zone:
                change_colour = not change_colour
                in_switch_zone = True
        else:
            in_switch_zone = False

        if change_colour:
            x_values_white.append(x)
            y_values_white.append(y)
        else:
            x_values.append(x)
            y_values.append(y)

plt.figure(figsize=(10, 10))
plt.scatter(x_values, y_values, color='black')

plt.gca().invert_yaxis()

plt.savefig('wacom.png', bbox_inches='tight')
