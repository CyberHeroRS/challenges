import os
import subprocess
import tempfile
import glob
import re

import requests
from PIL import Image
import numpy as np

HOST = os.environ.get("SERVICE_SIX_SEVEN_HTTP_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_SIX_SEVEN_HTTP_PORT", "80")
BASE_URL = f"http://{HOST}:{PORT}"

# The service renders the flag as a silent-film-style morse code video:
# a "left hand" gesture gif plays for each dash, a "right hand" gesture
# gif for each dot, with neutral (idle-pose) frames padding between
# symbols (short gap) and between letters (long gap). Only non-alphanumeric
# characters are stripped before encoding, so the decoded text includes
# the literal "SCC" + body letters/digits run together with no braces.
#
# Reference frames for both gestures (source/gesture_LEFT.gif,
# gesture_RIGHT.gif) are bind-mounted in at test time. Within each
# gesture's own frame sequence, the FIRST/LAST frames are themselves
# nearly identical to the neutral pose (used as padding filler too), so
# classifying by raw nearest-neighbor across all frames is ambiguous;
# only the *middle* frames of each gesture are visually distinctive
# enough to reliably detect, which is what this compares against.

MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}
REV_MORSE = {v: k for k, v in MORSE_CODE.items()}


def load_gif_frames(path):
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frames.append(np.array(gif.copy().convert("RGB"), dtype=np.int32))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


def mse(a, b):
    return np.mean((a - b) ** 2)


def main():
    r = requests.get(f"{BASE_URL}/67.mp4", timeout=30)
    r.raise_for_status()

    with tempfile.TemporaryDirectory() as tmp:
        video_path = os.path.join(tmp, "67.mp4")
        with open(video_path, "wb") as f:
            f.write(r.content)

        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, os.path.join(tmp, "f_%05d.png")],
            check=True, capture_output=True,
        )
        frame_files = sorted(glob.glob(os.path.join(tmp, "f_*.png")))

        left = load_gif_frames("/mounts/gesture_LEFT.gif")
        right = load_gif_frames("/mounts/gesture_RIGHT.gif")

        THRESH = 500
        labels = []
        for fpath in frame_files:
            vf = np.array(Image.open(fpath).convert("RGB"), dtype=np.int32)
            d_left_active = min(mse(vf, left[i]) for i in range(1, len(left) - 1))
            d_right_active = mse(vf, right[1])
            if d_left_active < THRESH:
                labels.append("L")
            elif d_right_active < THRESH:
                labels.append("R")
            else:
                labels.append("N")

    # compress to runs
    runs = []
    cur, count = labels[0], 1
    for c in labels[1:]:
        if c == cur:
            count += 1
        else:
            runs.append((cur, count))
            cur, count = c, 1
    runs.append((cur, count))

    symbols = []
    letters_syms = []
    for typ, cnt in runs:
        if typ == "N":
            if cnt >= 8 and symbols:
                letters_syms.append(symbols)
                symbols = []
        elif typ == "L":
            symbols.append("-")
        elif typ == "R":
            symbols.append(".")
    if symbols:
        letters_syms.append(symbols)

    decoded = "".join(REV_MORSE.get("".join(s), "?") for s in letters_syms)
    print(f"Decoded: {decoded}")

    # The decoded stream is the flag's "SCC" + body run together with no
    # braces (only non-alphanumeric chars were stripped before encoding).
    # Reconstruct the proper SCC{...} form for the Dockerfile's own
    # grep-based pass/fail check.
    body = decoded[3:] if decoded.startswith("SCC") else decoded
    print(f"SCC{{{body}}}")

    flag_env = os.environ.get("flag_flag")
    if flag_env:
        expected = re.sub(r"[^A-Za-z0-9]", "", flag_env.upper())
        if expected not in decoded:
            raise SystemExit(f"flag mismatch: expected {expected!r} to be in {decoded!r}")


if __name__ == "__main__":
    main()
