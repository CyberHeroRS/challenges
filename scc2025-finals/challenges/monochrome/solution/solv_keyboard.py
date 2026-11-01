#!/usr/bin/python
import os

KEY_CODES = {
    0x04:['a', 'A'],
    0x05:['b', 'B'],
    0x06:['c', 'C'],
    0x07:['d', 'D'],
    0x08:['e', 'E'],
    0x09:['f', 'F'],
    0x0A:['g', 'G'],
    0x0B:['h', 'H'],
    0x0C:['i', 'I'],
    0x0D:['j', 'J'],
    0x0E:['k', 'K'],
    0x0F:['l', 'L'],
    0x10:['m', 'M'],
    0x11:['n', 'N'],
    0x12:['o', 'O'],
    0x13:['p', 'P'],
    0x14:['q', 'Q'],
    0x15:['r', 'R'],
    0x16:['s', 'S'],
    0x17:['t', 'T'],
    0x18:['u', 'U'],
    0x19:['v', 'V'],
    0x1A:['w', 'W'],
    0x1B:['x', 'X'],
    0x1C:['y', 'Y'],
    0x1D:['z', 'Z'],
    0x1E:['1', '!'],
    0x1F:['2', '@'],
    0x20:['3', '#'],
    0x21:['4', '$'],
    0x22:['5', '%'],
    0x23:['6', '^'],
    0x24:['7', '&'],
    0x25:['8', '*'],
    0x26:['9', '('],
    0x27:['0', ')'],
    0x28:['\n','\n'],
    0x29:['␛','␛'],
    0x2a:['⌫', '⌫'],
    0x2b:['\t','\t'],
    0x2C:[' ', ' '],
    0x2D:['-', '_'],
    0x2E:['=', '+'],
    0x2F:['[', '{'],
    0x30:[']', '}'],
    0x32:['#','~'],
    0x33:[';', ':'],
    0x34:['\'', '"'],
    0x36:[',', '<'],
    0x37:['.', '>'],
    0x38:['/', '?'],
    0x39:['⇪','⇪'],
    0x4f:[u'→',u'→'],
    0x50:[u'←',u'←'],
    0x51:[u'↓',u'↓'],
    0x52:[u'↑',u'↑']
}

os.system("""tshark -r capture.pcapng -Y 'usbhid.data && usb.data_len == 8' -T fields -e usbhid.data | sed 's/../:&/g2' > keyboard.txt""")

cursor_x = 0
cursor_y = 0
lines = [""]
output = ""
skip_next = False

for line in open('keyboard.txt').readlines():
    l = line.strip().split(":")
    shift = int(l[0], 16)
    key = int(l[2], 16)

    if skip_next:
        skip_next = False
        continue

    if key == 0 or int(l[3], 16) > 0:
        continue

    if not key in KEY_CODES:
        continue

    if shift != 0:
        shift=1
        skip_next = True

    if KEY_CODES[key][shift] == u'↑':
        lines[cursor_y] += output
        output = ''
        cursor_y -= 1
    
    elif KEY_CODES[key][shift] == u'↓':
        lines[cursor_y] += output
        output = ''
        cursor_y += 1

    elif KEY_CODES[key][shift] == u'→':
        cursor_x += 1

    elif KEY_CODES[key][shift] == u'←':
        cursor_x -= 1

    elif KEY_CODES[key][shift] == '\n':
        lines.append("")
        lines[cursor_y] += output
        cursor_x = 0
        cursor_y += 1
        output = ''

    elif KEY_CODES[key][shift] == '[BACKSPACE]':
        output = output[:cursor_x-1] + output[cursor_x:]
        cursor_x -= 1
    
    else:
        output = output[:cursor_x] + KEY_CODES[key][shift] + output[cursor_x:]
        cursor_x += 1

if lines == [""]:
    lines[0] = output

if output != '' and output not in lines:
    lines[cursor_y] += output
    
print('\n'.join(lines))