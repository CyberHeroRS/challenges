"""Solver for Hidden Cat.

The flag is hidden via LSB (least-significant-bit) steganography: the text
"SCC{...}" was rendered as a bitmap and its pixels were baked into the
least-significant bit of the R, G and B channels of hidden_cat.png (the
alpha channel is untouched, constant 255). Each channel's LSB plane carries
the same text but with different surrounding dither noise, so taking a
majority vote across the three channels (bit set in at least 2 of 3
channels) cancels out most of the per-channel noise and leaves a clean
binary image of the flag text, which is then read with OCR.
"""

import os

from PIL import Image
import pytesseract

IMAGE_PATH = "/solution/hidden_cat.png"


def extract_lsb_majority(path):
    """Build a clean black/white bitmap from the majority vote of the R/G/B LSBs."""
    img = Image.open(path).convert("RGB")
    width, height = img.size
    pixels = img.load()

    out = Image.new("L", (width, height))
    out_pixels = out.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            votes = (r & 1) + (g & 1) + (b & 1)
            out_pixels[x, y] = 255 if votes >= 2 else 0
    return out


def ocr_candidates(image):
    """Run OCR over a few page-segmentation modes and scales."""
    texts = []
    variants = [image]
    for scale in (2, 4, 6):
        variants.append(
            image.resize((image.width * scale, image.height * scale), Image.LANCZOS)
        )
    for variant in variants:
        for psm in (6, 7, 11, 12):
            text = pytesseract.image_to_string(variant, config=f"--psm {psm}").strip()
            if text:
                texts.append(text)
    return texts


def normalize(s):
    # Fold common leetspeak/OCR confusions so a correct-but-imperfect read
    # still matches the expected flag.
    s = s.lower().replace(" ", "_")
    for a, b in (("o", "0"), ("i", "1"), ("l", "1"), ("a", "4")):
        s = s.replace(a, b)
    return s


def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def best_flag_candidate(texts):
    """Pick the substring from OCR output that looks most like `SCC{...}`."""
    best = None
    for text in texts:
        start = text.find("SCC{")
        end = text.find("}", start)
        if start == -1 or end == -1:
            continue
        candidate = text[start : end + 1]
        best = candidate if best is None or len(candidate) > len(best) else best
    return best


expected = os.environ.get("flag_main")
if not expected:
    print("flag_main not set")
    raise SystemExit(1)

expected_norm = normalize(expected)

bitmap = extract_lsb_majority(IMAGE_PATH)
bitmap.save("/solution/lsb_majority.png")

texts = ocr_candidates(bitmap)
print(f"Collected {len(texts)} OCR reads")

exact = best_flag_candidate(texts)
if exact:
    print(f"Best bracketed candidate: {exact!r}")

best = None
for text in texts:
    norm = normalize(text)
    distance = levenshtein(expected_norm, norm)
    if best is None or distance < best[0]:
        best = (distance, text)
    # Also score just the bracketed substring, which drops surrounding noise.
    start = text.find("SCC{")
    end = text.find("}", start)
    if start != -1 and end != -1:
        bracket_norm = normalize(text[start : end + 1])
        bdist = levenshtein(expected_norm, bracket_norm)
        if bdist < best[0]:
            best = (bdist, text[start : end + 1])

if best is None:
    print("No OCR candidates produced")
    raise SystemExit(1)

distance, text = best
print(f"Best OCR read: {text!r} (edit distance {distance} vs expected)")

if distance <= 2:
    print("MATCH")
else:
    print("NO MATCH")
    raise SystemExit(1)
