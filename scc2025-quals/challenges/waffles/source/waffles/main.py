from flask import Flask, render_template, send_file
import os
from PIL import Image, ImageDraw, ImageFont, ImageFont
from io import BytesIO

app = Flask(__name__, static_folder="public", static_url_path="/public")

WAFFLES = [
    {
        "name": "Classic Belgian",
        "image": "classic-belgian.jpg",
        "description": "Light and airy Belgian waffle with deep pockets",
    },
    {
        "name": "Liège Waffle",
        "image": "liege.jpg",
        "description": "Thick, sweet Belgian waffle with caramelized sugar",
    },
    {
        "name": "American Waffle",
        "image": "american.jpg",
        "description": "Thin, round waffle often served with butter and syrup",
    },
    {
        "name": "Stroopwafel",
        "image": "stroopwafel.jpg",
        "description": "Thin Dutch waffle cookie filled with caramel syrup",
    },
    {
        "name": "Chocolate Chip",
        "image": "chocolate-chip.jpg",
        "description": "Belgian waffle loaded with chocolate chips",
    },
    {
        "name": "Pandan Waffle",
        "image": "panda.jpg",
        "description": "Green Vietnamese waffle flavored with pandan and coconut",
    },
    {
        "name": "Swedish Waffle",
        "image": "swedish.jpg",
        "description": "Thin, heart-shaped waffle often served with jam",
    },
    {
        "name": "Pizzelle",
        "image": "pizzelle.jpg",
        "description": "Thin, crisp Italian waffle cookie often flavored with anise",
    },
    {
        "name": "Flag Waffle",
        "image": "flag.jpg",
        "description": "The best waffle for CTF players",
    },
]


@app.route("/")
def gallery():
    return render_template("gallery.html", waffles=WAFFLES)


@app.route("/public/flag.jpg")
def flag():
    flag = os.getenv("FLAG", "SCC{fake_flag}")

    img = Image.new("RGB", (400, 100), color="white")
    d = ImageDraw.Draw(img)

    font_size = 1
    while True:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        text_width = d.textlength(flag, font=font)
        text_height = font.size

        if text_width > img.width * 0.9 or text_height > img.height * 0.9:
            font_size -= 1
            break
        font_size += 1

    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    text_width = d.textlength(flag, font=font)

    x = (img.width - text_width) // 2
    y = (img.height - font.size) // 2

    d.text((x, y), flag, fill="black", font=font)

    img_io = BytesIO()
    img.save(img_io, "JPEG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(port=3000, host="0.0.0.0")
