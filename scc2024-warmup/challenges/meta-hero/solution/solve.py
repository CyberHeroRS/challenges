"""
Solver for "Meta Hero".

Vulnerability: the challenge PNG carries hidden tEXt metadata chunks.
A "Description" chunk openly hints that the flag is stashed in the
"Author" chunk, obfuscated by interleaving it with itself character by
character. Reading every second character of the "Author" field (i.e.
indices 0, 2, 4, ...) recovers the real flag - just like `exiftool` would
show when dumping the PNG's text metadata.
"""

from PIL import Image


def main():
    image = Image.open("public/meta_hero.png")
    author = image.text["Author"]
    flag = author[::2]
    print(flag)


if __name__ == "__main__":
    main()
