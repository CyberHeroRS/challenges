import os

import requests
from PIL import Image
import numpy as np

HOST = os.environ.get("SERVICE_BRAINROT_69_WEB_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_BRAINROT_69_WEB_PORT", "80")
BASE_URL = f"http://{HOST}:{PORT}"

IMAGES_DIR = "/mounts/images"
TARGET_HEIGHT = 360

# The service renders the flag as a horizontal strip of 256 possible
# "brainrot" meme images (source/images/<index>_<name>.<ext>), each
# resized to a fixed height (aspect ratio preserved, so width varies per
# image). Per-character encoding: mirror the bit order of the ASCII
# byte, then add 69 mod 256, and use that as the image index -- so
# decoding is just reversing those two steps once each image segment's
# index is identified.
#
# Since every image is deterministically resized with Lanczos
# resampling to the exact same reference set bundled with the
# challenge (bind-mounted in at test time), segments can be identified
# via exact pixel match: scan left-to-right, and at each position find
# which reference image (by width) produces a zero/near-zero MSE
# against the live image at that offset, consume its width, and
# continue.


def mirror_bits(byte):
    result = 0
    for i in range(8):
        if byte & (1 << i):
            result |= 1 << (7 - i)
    return result


def decode_index(idx):
    mirrored = (idx - 69) % 256
    return mirror_bits(mirrored)


def get_image_map():
    image_map = {}
    for f in os.listdir(IMAGES_DIR):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            try:
                index = int(f.split("_")[0])
                image_map[index] = os.path.join(IMAGES_DIR, f)
            except (ValueError, IndexError):
                pass
    return image_map


def load_and_resize_image(filepath):
    img = Image.open(filepath)
    if img.mode in ("RGBA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")
    ratio = TARGET_HEIGHT / img.height
    new_width = int(img.width * ratio)
    img = img.resize((new_width, TARGET_HEIGHT), Image.LANCZOS)
    return np.array(img, dtype=np.int32)


def main():
    r = requests.get(f"{BASE_URL}/encoded.png", timeout=30)
    r.raise_for_status()
    with open("/tmp/encoded.png", "wb") as f:
        f.write(r.content)

    image_map = get_image_map()
    ref_arrays = {idx: load_and_resize_image(path) for idx, path in image_map.items()}

    combined = np.array(Image.open("/tmp/encoded.png").convert("RGB"), dtype=np.int32)
    H, W, _ = combined.shape

    x = 0
    decoded_chars = []
    while x < W:
        best_idx, best_err, best_w = None, None, None
        for idx, arr in ref_arrays.items():
            w = arr.shape[1]
            if x + w > W:
                continue
            segment = combined[:, x : x + w, :]
            err = np.mean((segment.astype(np.int64) - arr.astype(np.int64)) ** 2)
            if best_err is None or err < best_err:
                best_idx, best_err, best_w = idx, err, w
        if best_idx is None:
            break
        decoded_chars.append(chr(decode_index(best_idx)))
        x += best_w

    flag = "".join(decoded_chars)
    print(f"Decoded: {flag}")

    flag_env = os.environ.get("flag_flag")
    if flag_env and flag_env not in flag:
        raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")


if __name__ == "__main__":
    main()
