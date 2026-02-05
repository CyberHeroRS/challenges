from itertools import product
from PIL import Image
import curses
from pwn import *


class DeadException(Exception):
    pass


img = Image.open("arena.png")
print(f"Image size: {img.size}")
filebuf = open("moves.txt", "r").read()
player = (0, 0)
end = (0, 0)
arena = [[" " for _ in range(img.size[1])] for _ in range(img.size[0])]
for xy in product(range(img.size[0]), range(img.size[1])):
    pixel = img.getpixel(xy)
    x, y = xy
    if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0 and pixel[3] == 255:
        arena[x][y] = "#"
    # if pixel[0] == 91 and pixel[1] == 110 and pixel[2] == 225 and pixel[3] == 255:
    #     player = xy
    #     arena[x][y] = '@'
    if pixel[0] == 118 and pixel[1] == 66 and pixel[2] == 138 and pixel[3] == 255:
        end = xy
        arena[x][y] = "X"

p = process("./target/release/wwwwww")
# Haha guess what. You have to let the process initialize
# or you're going to get very strange results!
sleep(0.1)
SECTION_LOC = next(
    int(x.split("-", 1)[0], 16)
    for x in open(f"/proc/{p.proc.pid}/maps").readlines()
    if p.elf.path in x and "rw" in x
)


def get_player():
    if p.proc.poll() != None:
        raise DeadException()
    try:
        x = p.leak(SECTION_LOC + 8, 1)[0]  # Leak x
        y = p.leak(SECTION_LOC + 9, 1)[0]  # Leak y
        arena[x][y] = "@"
        return (x, y)
    except:
        raise DeadException()


scr = curses.initscr()
# gravity = 1
# won = False
try:
    # p.sendline(buf.encode())
    buf = ""
    player = get_player()
    for c in filebuf:
        p.sendline(c)
        player = get_player()
        buf += c  # Only append on a successful move

    while True:
        for x, y in product(range(img.size[0]), range(img.size[1])):
            scr.addch(y, x, arena[x][y])
        c = scr.getkey()
        if c == "q":
            break
        if c not in "wasd":
            continue
        x, y = player
        arena[x][y] = " "
        p.sendline(c.encode())
        x, y = player = get_player()
        buf += c
        # if c == 'w':
        #     gravity = -gravity
        #     continue
        # if c == 'a':
        #     player = (x := x - 1, y)
        # elif c == 'd':
        #     player = (x := x + 1, y)
        # player = (x, y := (y + gravity) % 32)
        # if arena[x][y] == "#":
        #     break
        # if arena[x][y] == "X":
        #     won = True
        #     break
        arena[x][y] = "@"

except (KeyboardInterrupt, DeadException):
    pass
finally:
    curses.endwin()

# if won:
#     print("You won!")
# else:
#     print("Dead")
info("Game over")
success("stdout: " + p.recvall(0.2).decode())
open("moves.txt", "w").write(buf)
