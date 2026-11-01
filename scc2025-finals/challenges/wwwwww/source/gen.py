from PIL import Image
from itertools import product

img = Image.open("arena.png")
print(f"Image dim: {img.size}")
c = ""
player_start = ()
maze_end = ()
for xy in product(range(img.size[0]), range(img.size[1])):
    p = img.getpixel(xy)
    if p[0] == 0 and p[1] == 0 and p[2] == 0 and p[3] == 255:
        c += f"({xy[0]}, {xy[1]}) | "
    if p[0] == 91 and p[1] == 110 and p[2] == 225 and p[3] == 255:
        player_start = xy
    if p[0] == 118 and p[1] == 66 and p[2] == 138 and p[3] == 255:
        maze_end = xy

print(f"Player start: {player_start}")
print(f"End: {maze_end}")
open("src/arena.rs", "w").write(f"""\
pub const PLAYER_START: (u8, u8) = {player_start};
pub const BABA_IS_WIN: (u8, u8) = {maze_end};

#[macro_export]
macro_rules! check_pos {{
    ( $x:ident ) => {{
        {{
            match $x {{
                {c.rstrip('| ')} => false,
                _ => true
            }}
        }}
    }};
}}
""")
