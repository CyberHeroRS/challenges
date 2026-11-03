"""Solver for Art.

The flag is not hidden invisibly in the pixel data (no LSB steganography, no
appended/trailing bytes after the PNG IEND chunk, no EXIF/text chunks) -- it
is hidden in plain sight as four different classic "secret message" ciphers
rendered as visible glyphs/shapes directly on the painted canvas inside the
artwork:

  1. Two lines of Morse code (dots/dashes, with "/" used as a few explicit
     letter separators) -> decodes to the first flag word, e.g. "d3c0d1n6".
  2. A row of Braille dots -> decodes letter-by-letter; whenever a decoded
     Braille letter falls in a-j it is rendered as the corresponding Braille
     "number" (a=1 ... j=0, the standard Braille numeral convention), giving
     the second flag word, e.g. "m3554635".
  3. A Brainfuck program (rendered using +-><[]. glyphs) -> executing it
     produces the third flag word, e.g. "15".
  4. Three solid color swatches -> each channel byte of each swatch's RGB is
     an ASCII character code; reading R,G,B of swatch 1, then swatch 2, then
     swatch 3 spells the fourth flag word, e.g. "b34u71ful".

Each piece is extracted from the real pixels of public/art.png using simple
connected-component analysis (BFS flood fill over thresholded dark pixels),
not hardcoded coordinates of characters.
"""

import os
from collections import deque

from PIL import Image

IMAGE_PATH = "/solution/art.png"
DARK_THRESHOLD = 60

# Region of the canvas that holds all four hidden-message elements, found by
# locating the painting in the artwork. Generous margins are used so small
# rendering differences don't clip any glyph.
CANVAS_X = (700, 1120)
MORSE_Y = (300, 370)
BRAILLE_Y = (385, 450)
BRAINFUCK_Y = (470, 585)


def load_gray():
    return Image.open(IMAGE_PATH).convert("L")


def load_rgb():
    return Image.open(IMAGE_PATH).convert("RGB")


def connected_components(mask):
    """BFS 8-connected components over a boolean 2D list/array. Returns list
    of dicts with bounding box and the cropped boolean mask."""
    height = len(mask)
    width = len(mask[0]) if height else 0
    visited = [[False] * width for _ in range(height)]
    components = []
    for y in range(height):
        for x in range(width):
            if mask[y][x] and not visited[y][x]:
                queue = deque([(y, x)])
                visited[y][x] = True
                pixels = []
                while queue:
                    cy, cx = queue.popleft()
                    pixels.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if (
                                0 <= ny < height
                                and 0 <= nx < width
                                and mask[ny][nx]
                                and not visited[ny][nx]
                            ):
                                visited[ny][nx] = True
                                queue.append((ny, nx))
                ys = [p[0] for p in pixels]
                xs = [p[1] for p in pixels]
                y0, y1 = min(ys), max(ys)
                x0, x1 = min(xs), max(xs)
                cropped = [row[x0 : x1 + 1] for row in mask[y0 : y1 + 1]]
                components.append(
                    {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "mask": cropped}
                )
    return components


def dark_mask(gray_img, x_range, y_range):
    x0, x1 = x_range
    y0, y1 = y_range
    pixels = gray_img.load()
    mask = []
    for y in range(y0, y1):
        row = [pixels[x, y] < DARK_THRESHOLD for x in range(x0, x1)]
        mask.append(row)
    return mask, x0, y0


# --------------------------------------------------------------------------
# 1. Morse code
# --------------------------------------------------------------------------

MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}
MORSE_LOOKUP = {v: k for k, v in MORSE_CODE.items()}
MORSE_CODE_LENGTHS = sorted({len(code) for code in MORSE_LOOKUP}, reverse=True)


def char_type(ch):
    return "digit" if ch.isdigit() else "letter"


def all_min_token_decompositions(sequence):
    """Return every decomposition of `sequence` (a string of '.'/'-') into
    valid Morse characters that uses the fewest possible characters."""
    n = len(sequence)
    best_len = {0: 0}
    decompositions = {0: [[]]}
    for i in range(1, n + 1):
        options = []
        for length in MORSE_CODE_LENGTHS:
            start = i - length
            if start < 0 or start not in best_len:
                continue
            code = sequence[start:i]
            if code in MORSE_LOOKUP:
                options.append((start, MORSE_LOOKUP[code]))
        if not options:
            continue
        min_tokens = min(best_len[start] + 1 for start, _ in options)
        best_len[i] = min_tokens
        decompositions[i] = [
            prefix + [letter]
            for start, letter in options
            if best_len[start] + 1 == min_tokens
            for prefix in decompositions[start]
        ]
    if n not in decompositions:
        raise ValueError(f"No valid Morse decomposition for {sequence!r}")
    return decompositions[n]


def decode_morse_line(symbols_by_group):
    """`symbols_by_group` is a list of morse strings, one per slash-delimited
    segment of a single line. The outer (first/last) segments are expected to
    be exactly one character; inner segments may need disambiguation, which
    we resolve by requiring letters and digits to alternate across the whole
    line (a pattern that holds for every line in this artwork and is
    determined purely from the unambiguous outer characters, never from the
    target flag text)."""
    decoded_groups = [all_min_token_decompositions(seg) for seg in symbols_by_group]

    # Flatten all combinations and keep the ones consistent with strict
    # letter/digit alternation across the whole line.
    def combine(groups):
        if not groups:
            yield []
            return
        for option in groups[0]:
            for rest in combine(groups[1:]):
                yield option + rest

    candidates = list(combine(decoded_groups))
    alternating = [
        candidate
        for candidate in candidates
        if all(
            char_type(candidate[i]) != char_type(candidate[i + 1])
            for i in range(len(candidate) - 1)
        )
    ]
    chosen = alternating[0] if alternating else candidates[0]
    return "".join(chosen)


def extract_morse_symbols(gray_img):
    mask, ox, oy = dark_mask(gray_img, CANVAS_X, MORSE_Y)
    components = connected_components(mask)
    for comp in components:
        comp["x0"] += ox
        comp["x1"] += ox
        comp["y0"] += oy
        comp["y1"] += oy

    def height(c):
        return c["y1"] - c["y0"] + 1

    def width(c):
        return c["x1"] - c["x0"] + 1

    slashes = [c for c in components if height(c) >= 10]
    y_mid_values = sorted({c["y0"] for c in components if height(c) < 10})
    # Two clusters of y0 values -> two morse lines.
    line_split = (min(y_mid_values) + max(y_mid_values)) / 2

    lines = []
    for is_second in (False, True):
        symbols = sorted(
            (
                c
                for c in components
                if height(c) < 10 and ((c["y0"] >= line_split) == is_second)
            ),
            key=lambda c: c["x0"],
        )
        line_slashes = sorted(
            (
                s
                for s in slashes
                if (
                    (s["y0"] + s["y1"]) / 2 >= MORSE_Y[0]
                    and (s["y0"] + s["y1"]) / 2 < MORSE_Y[1]
                )
                and ((s["y0"] >= line_split) == is_second or s["y1"] >= line_split)
            ),
            key=lambda c: c["x0"],
        )
        # Keep only slashes whose vertical extent overlaps this line's band.
        band = (
            (min(c["y0"] for c in symbols), max(c["y1"] for c in symbols))
            if symbols
            else (0, 0)
        )
        line_slashes = [
            s for s in line_slashes if s["y0"] <= band[1] and s["y1"] >= band[0]
        ]
        slash_x = sorted(s["x0"] for s in line_slashes)

        groups = [[]]
        for sym in symbols:
            while slash_x and sym["x0"] > slash_x[0]:
                groups.append([])
                slash_x.pop(0)
            groups[-1].append("-" if width(sym) >= 10 else ".")
        lines.append(["".join(g) for g in groups])
    return lines


def solve_morse():
    gray_img = load_gray()
    lines = extract_morse_symbols(gray_img)
    return "".join(decode_morse_line(line) for line in lines).lower()


# --------------------------------------------------------------------------
# 2. Braille
# --------------------------------------------------------------------------

BRAILLE_MAP = {
    frozenset([1]): "a", frozenset([1, 2]): "b", frozenset([1, 4]): "c",
    frozenset([1, 4, 5]): "d", frozenset([1, 5]): "e", frozenset([1, 2, 4]): "f",
    frozenset([1, 2, 4, 5]): "g", frozenset([1, 2, 5]): "h", frozenset([2, 4]): "i",
    frozenset([2, 4, 5]): "j", frozenset([1, 3]): "k", frozenset([1, 2, 3]): "l",
    frozenset([1, 3, 4]): "m", frozenset([1, 3, 4, 5]): "n", frozenset([1, 3, 5]): "o",
    frozenset([1, 2, 3, 4]): "p", frozenset([1, 2, 3, 4, 5]): "q",
    frozenset([1, 2, 3, 5]): "r", frozenset([2, 3, 4]): "s", frozenset([2, 3, 4, 5]): "t",
    frozenset([1, 3, 6]): "u", frozenset([1, 2, 3, 6]): "v", frozenset([2, 4, 5, 6]): "w",
    frozenset([1, 3, 4, 6]): "x", frozenset([1, 3, 4, 5, 6]): "y", frozenset([1, 3, 5, 6]): "z",
}
# Standard Braille numeral convention: letters a-j double as digits 1-0.
BRAILLE_LETTER_TO_DIGIT = {
    "a": "1", "b": "2", "c": "3", "d": "4", "e": "5",
    "f": "6", "g": "7", "h": "8", "i": "9", "j": "0",
}


def solve_braille():
    gray_img = load_gray()
    mask, ox, oy = dark_mask(gray_img, CANVAS_X, BRAILLE_Y)
    components = connected_components(mask)
    dots = []
    for c in components:
        xc = ox + (c["x0"] + c["x1"]) / 2
        yc = oy + (c["y0"] + c["y1"]) / 2
        dots.append((xc, yc))
    dots.sort()

    # Cluster dots into Braille cells by horizontal gap.
    cells = []
    current = [dots[0]]
    for dot in dots[1:]:
        if dot[0] - current[-1][0] > 25:
            cells.append(current)
            current = [dot]
        else:
            current.append(dot)
    cells.append(current)

    row_ys = sorted({round(y, 1) for _, y in dots})
    # Merge nearby row values (anti-aliasing jitter) into up to 3 rows.
    rows = []
    for y in row_ys:
        if not rows or y - rows[-1] > 8:
            rows.append(y)
    assert len(rows) <= 3, f"expected at most 3 braille dot rows, got {rows}"

    def row_index(y):
        return min(range(len(rows)), key=lambda i: abs(rows[i] - y))

    result = []
    for cell in cells:
        x_min = min(x for x, _ in cell)
        dot_numbers = set()
        for x, y in cell:
            col = 0 if abs(x - x_min) < 5 else 1
            dot_numbers.add(row_index(y) + 1 if col == 0 else row_index(y) + 4)
        letter = BRAILLE_MAP[frozenset(dot_numbers)]
        result.append(BRAILLE_LETTER_TO_DIGIT.get(letter, letter))
    return "".join(result)


# --------------------------------------------------------------------------
# 3. Brainfuck
# --------------------------------------------------------------------------


def classify_brainfuck_glyph(comp):
    mask = comp["mask"]
    height = len(mask)
    width = len(mask[0])
    if height >= 18:
        left = sum(row[: max(1, width // 3)].count(True) for row in mask)
        right = sum(row[-max(1, width // 3) :].count(True) for row in mask)
        return "[" if left > right else "]"
    if height <= 6:
        return "." if width <= 5 else "-"
    mid_row = mask[height // 2]
    mid_col = [row[width // 2] for row in mask]
    has_hbar = mid_row.count(True) >= width * 0.7
    has_vbar = mid_col.count(True) >= height * 0.7
    if has_hbar and has_vbar:
        return "+"
    top_row, bottom_row = mask[0], mask[-1]
    left_score = top_row[: width // 2].count(True) + bottom_row[: width // 2].count(True)
    right_score = top_row[width // 2 :].count(True) + bottom_row[width // 2 :].count(True)
    return ">" if left_score > right_score else "<"


def run_brainfuck(code):
    tape = [0] * 30000
    ptr = 0
    out = []
    jump = {}
    stack = []
    for idx, ch in enumerate(code):
        if ch == "[":
            stack.append(idx)
        elif ch == "]":
            start = stack.pop()
            jump[start] = idx
            jump[idx] = start
    i = 0
    while i < len(code):
        ch = code[i]
        if ch == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif ch == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif ch == ">":
            ptr += 1
        elif ch == "<":
            ptr -= 1
        elif ch == ".":
            out.append(chr(tape[ptr]))
        elif ch == "[" and tape[ptr] == 0:
            i = jump[i]
        elif ch == "]" and tape[ptr] != 0:
            i = jump[i]
        i += 1
    return "".join(out)


def solve_brainfuck():
    gray_img = load_gray()
    mask, ox, oy = dark_mask(gray_img, CANVAS_X, BRAINFUCK_Y)
    components = connected_components(mask)
    for comp in components:
        comp["x0"] += ox
        comp["x1"] += ox
        comp["y0"] += oy
        comp["y1"] += oy

    # Group components into lines by clustering their vertical center (not
    # y0): short glyphs like "-" and "." sit at the same text baseline as
    # the full-height "+"/"<"/">" glyphs on their line but have a smaller
    # bounding box, so y0 alone can misclassify them into the wrong line.
    def center(c):
        return (c["y0"] + c["y1"]) / 2

    components.sort(key=center)
    lines = []
    current = [components[0]]
    for comp in components[1:]:
        if center(comp) - center(current[-1]) > 15:
            lines.append(current)
            current = [comp]
        else:
            current.append(comp)
    lines.append(current)

    code = ""
    for row in lines:
        row.sort(key=lambda c: c["x0"])
        code += "".join(classify_brainfuck_glyph(c) for c in row)

    return run_brainfuck(code)


# --------------------------------------------------------------------------
# 4. Color swatches
# --------------------------------------------------------------------------


def solve_colors():
    rgb_img = load_rgb()
    width, height = rgb_img.size
    pixels = rgb_img.load()

    # Find solid-color blocks against the near-white canvas background by
    # counting pixel-color frequency restricted to the lower part of the
    # painting (below the Brainfuck text, above the canvas edge).
    from collections import Counter

    counts = Counter()
    y0, y1 = 580, min(height, 700)
    x0, x1 = CANVAS_X
    for y in range(y0, y1):
        for x in range(x0, min(width, x1)):
            counts[pixels[x, y]] += 1

    # The three swatches are large uniform blocks; the near-white background
    # varies pixel-to-pixel (soft gradient/noise) so it never repeats enough
    # to compete with them.
    swatch_colors = [color for color, _ in counts.most_common(3)]

    # Order swatches left-to-right by locating one representative pixel of
    # each color.
    def first_x(color):
        for y in range(y0, y1):
            for x in range(x0, min(width, x1)):
                if pixels[x, y] == color:
                    return x
        return 10**9

    swatch_colors.sort(key=first_x)

    chars = []
    for color in swatch_colors:
        chars.extend(chr(component) for component in color)
    return "".join(chars)


def main():
    expected = os.environ.get("flag_main")
    if not expected:
        print("flag_main not set")
        raise SystemExit(1)

    word1 = solve_morse()
    word2 = solve_braille()
    word3 = solve_brainfuck()
    word4 = solve_colors()

    print(f"Morse code          -> {word1!r}")
    print(f"Braille             -> {word2!r}")
    print(f"Brainfuck output    -> {word3!r}")
    print(f"Color swatch ASCII  -> {word4!r}")

    flag = f"SCC{{{word1}_{word2}_{word3}_{word4}}}"
    print(f"Recovered flag: {flag}")
    print(f"Expected flag:  {expected}")

    if flag == expected:
        print("MATCH")
    else:
        print("NO MATCH")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
