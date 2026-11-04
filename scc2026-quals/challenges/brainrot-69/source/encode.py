#!/usr/bin/env python3
"""
Encode a flag into brainrot memes.

Encoding process for each character:
1. Get ASCII value (0-255)
2. Mirror bits (reverse bit order): 10101111 → 11110101
3. ROT69: add 69 mod 256
4. Use result as image index (1-256)
"""

import os
from PIL import Image

IMAGES_DIR = "/app/images"
OUTPUT_FILE = "/app/static/encoded.png"
TARGET_HEIGHT = 360


def mirror_bits(byte):
    """Mirror/reverse the bits in a byte: 10101111 → 11110101"""
    result = 0
    for i in range(8):
        if byte & (1 << i):
            result |= (1 << (7 - i))
    return result


def encode_char(char):
    """Encode a character: mirror bits, then ROT69."""
    value = ord(char)
    mirrored = mirror_bits(value)
    rotated = (mirrored + 69) % 256
    return rotated


def get_image_map():
    """Build a map of index -> image filepath."""
    image_map = {}
    for f in os.listdir(IMAGES_DIR):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            try:
                index = int(f.split('_')[0])
                image_map[index] = os.path.join(IMAGES_DIR, f)
            except (ValueError, IndexError):
                pass
    return image_map


def load_and_resize_image(filepath):
    """Load an image and resize to target height, preserving aspect ratio."""
    img = Image.open(filepath)
    
    if img.mode in ('RGBA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    ratio = TARGET_HEIGHT / img.height
    new_width = int(img.width * ratio)
    img = img.resize((new_width, TARGET_HEIGHT), Image.LANCZOS)
    
    return img


def encode_flag(flag):
    """Encode a flag string into brainrot meme images."""
    image_map = get_image_map()
    
    encoded_indices = []
    for char in flag:
        encoded = encode_char(char)
        encoded_indices.append(encoded)
    
    missing = [idx for idx in encoded_indices if idx not in image_map]
    if missing:
        print(f"ERROR: Missing images for indices: {missing}")
        return None
    
    images = []
    total_width = 0
    
    for idx in encoded_indices:
        img = load_and_resize_image(image_map[idx])
        images.append(img)
        total_width += img.width
    
    combined = Image.new('RGB', (total_width, TARGET_HEIGHT), (255, 255, 255))
    
    x_offset = 0
    for img in images:
        combined.paste(img, (x_offset, 0))
        x_offset += img.width
    
    return combined


def main():
    flag = os.environ.get('FLAG', 'SCC{brainrot_test_flag}')
    
    os.makedirs('/app/static', exist_ok=True)
    
    combined = encode_flag(flag)
    
    if combined:
        combined.save(OUTPUT_FILE, 'PNG', optimize=True, compress_level=9)
        print(f"Encoded flag to {OUTPUT_FILE}")
    else:
        print("Failed to encode flag!")
        exit(1)


if __name__ == "__main__":
    main()
