import os

from PIL import Image
import pytesseract

IMAGE_PATH = "/solution/monkey_magic.jpg"

# The distributed file has had the first 12 bytes of its JFIF header zeroed
# out: the SOI marker (FF D8), the APP0 marker + length (FF E0 00 10), the
# "JFIF\0" tag and the version-major byte all read as 00. Everything from
# byte 12 onward (version-minor, units, density, thumbnail dims and the rest
# of the JPEG stream, including a valid FF D9 EOI trailer) is untouched, so
# repairing the file is just restoring that standard 12-byte prefix.
STANDARD_HEADER_PREFIX = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01])


def repair_jpeg(path):
    with open(path, "rb") as f:
        data = bytearray(f.read())
    data[: len(STANDARD_HEADER_PREFIX)] = STANDARD_HEADER_PREFIX
    return bytes(data)


def get_flag_text(image_bytes):
    import io

    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    # The flag text is rendered small relative to the overall image, so
    # upscaling before OCR (same recovered pixels, just easier for tesseract
    # to read) substantially improves accuracy over running it on the raw
    # image directly - same trick used by the waffles/secret-archives solvers.
    image = image.resize((image.width * 4, image.height * 4), Image.BICUBIC)
    # The flag text is only a small region of a much larger photo, so the
    # default automatic page-segmentation mode (which locates text blocks
    # within the image) reads it reliably, whereas --psm 7 (which assumes the
    # *entire* image is one line of text) fails outright on this layout.
    return pytesseract.image_to_string(image).strip()


def normalize(s):
    # OCR of this leetspeak flag text reliably confuses 0/O, 1/I/l and 4/a,
    # and sometimes reads the underscores between words as spaces; fold
    # those together so a correct-but-imperfectly-OCR'd read still matches
    # the expected flag.
    s = s.lower().replace(" ", "_")
    for a, b in (("o", "0"), ("i", "1"), ("l", "1"), ("a", "4")):
        s = s.replace(a, b)
    return s


fixed = repair_jpeg(IMAGE_PATH)
with open("/solution/monkey_magic_fixed.jpg", "wb") as f:
    f.write(fixed)

flag_text = get_flag_text(fixed)
print(f"OCR read: {flag_text!r}")

expected = os.environ.get("flag_main")
if expected and normalize(expected) in normalize(flag_text):
    print("MATCH")
else:
    print("NO MATCH")
    raise SystemExit(1)
