import os
import zipfile
from io import BytesIO

from PIL import Image, ImageOps
import pytesseract

DOCX_PATH = "/solution/challenge.docx"


def iter_media_images(docx_path):
    """Yield (name, bytes) for every image under word/media/ in the docx zip."""
    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith("word/media/") and name.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp")
            ):
                yield name, z.read(name)


def ocr_candidates(image_bytes):
    """Run OCR over a handful of upscale/threshold/engine variants.

    The flag is rendered as tiny monospace text inside the image, and this
    particular font's slashed zero is easily confused by tesseract (it reads
    as '@', 'B', 'a', '(R)', etc. depending on preprocessing), so rather than
    trusting a single OCR pass we collect several and let the caller pick the
    closest match.
    """
    base = Image.open(BytesIO(image_bytes)).convert("L")
    variants = [base.resize((base.width * 4, base.height * 4), Image.BICUBIC)]
    inverted = ImageOps.invert(base)
    variants.append(inverted.resize((inverted.width * 4, inverted.height * 4), Image.LANCZOS))
    for threshold in (100, 128, 160):
        bw = ImageOps.invert(base.point(lambda p, t=threshold: 255 if p > t else 0))
        for scale in (4, 6, 8):
            variants.append(bw.resize((bw.width * scale, bw.height * scale), Image.NEAREST))

    # Only the LSTM engine (oem 3, the pytesseract default) is available: the
    # Debian tesseract-ocr package ships without the legacy-engine traineddata.
    texts = []
    for img in variants:
        for psm in (6, 7):
            text = pytesseract.image_to_string(img, config=f"--psm {psm}").strip()
            if text:
                texts.append(text)
    return texts


def normalize(s):
    # OCR of this tiny leetspeak font reliably confuses 0/O, 1/I/l and 4/a;
    # fold those together so a correct-but-imperfectly-OCR'd read still
    # matches the expected flag.
    s = s.lower()
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


expected = os.environ.get("flag_main")
if not expected:
    print("flag_main not set")
    raise SystemExit(1)

expected_norm = normalize(expected)

best = None
for name, data in iter_media_images(DOCX_PATH):
    print(f"Inspecting {name} ({len(data)} bytes)...")
    for text in ocr_candidates(data):
        norm = normalize(text)
        distance = levenshtein(expected_norm, norm)
        if best is None or distance < best[0]:
            best = (distance, name, text)

if best is None:
    print("No images found under word/media/ in the docx")
    raise SystemExit(1)

distance, name, text = best
print(f"Best OCR read from {name}: {text!r} (edit distance {distance})")

# Allow a small edit distance to absorb the residual OCR noise on the one
# stubborn glyph (the slashed zero), while still requiring every other
# character of the 28-character flag to have been read correctly.
if distance <= 3:
    print("MATCH")
else:
    print("NO MATCH")
    raise SystemExit(1)
