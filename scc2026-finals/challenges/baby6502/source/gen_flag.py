#!/usr/bin/env python3

import random
import re

KEY_SEED = 6502


def transform_byte(b: int, k: int, i: int) -> int:
    v = ((b ^ k) + 0x35 - (i * 5)) & 0xFF
    v = ((v << 1) | (v >> 7)) & 0xFF
    v ^= 0xA7
    return v


def untransform_byte(v: int, k: int, i: int) -> int:
    v ^= 0xA7
    v = ((v >> 1) | ((v & 1) << 7)) & 0xFF
    return ((v - 0x35 + (i * 5)) & 0xFF) ^ k


def ascii_to_petscii(text: str) -> bytes:
    petscii_bytes = bytearray()
    for char in text:
        ascii_val = ord(char)
        if 97 <= ascii_val <= 122:
            petscii_bytes.append(ascii_val - 32)
        elif 65 <= ascii_val <= 90:
            petscii_bytes.append(ascii_val + 128)
        elif ascii_val == 95: # _
            petscii_bytes.append(164)
        else:
            petscii_bytes.append(ascii_val)
    return bytes(petscii_bytes)


def petscii_to_ascii(petscii_bytes: bytes) -> str:
    ascii_chars = []
    for byte in petscii_bytes:
        if 65 <= byte <= 90:
            ascii_chars.append(chr(byte + 32))
        elif 193 <= byte <= 218:
            ascii_chars.append(chr(byte - 128))
        elif 97 <= byte <= 122:
            ascii_chars.append(chr(byte - 32))
        elif byte == 164: # _
            ascii_chars.append('_')
        else:
            ascii_chars.append(chr(byte))
    return "".join(ascii_chars)


def encrypt_flag(pt: str, key: bytes) -> bytes:
    raw = ascii_to_petscii(pt)
    return bytes(transform_byte(raw[i], key[i], i) for i in range(len(raw)))


def decrypt_flag(ct: bytes, key: bytes) -> str:
    raw = bytes(untransform_byte(ct[i], key[i], i) for i in range(len(ct)))
    return petscii_to_ascii(raw)


def to_c_byte_array(x: bytes) -> str:
    return "{ 0x" + x.hex(",").replace(",", ", 0x") + " }"


def main() -> None:
    flag = open("flag.txt", encoding="utf-8").read().strip()
    random.seed(KEY_SEED)
    key = random.randbytes(len(flag))

    flag_enc = encrypt_flag(flag, key)
    flag_dec = decrypt_flag(flag_enc, key)
    assert flag == flag_dec

    print("%-20.20s%s" % ("Flag:", flag))
    print("%-20.20s%s" % ("Key:", key.hex()))
    print("%-20.20s%s" % ("Encrypted:", flag_enc.hex()))

    c_prog = open("main.c", encoding="utf-8").read()
    c_prog = re.sub(r'"flag"', to_c_byte_array(flag_enc), c_prog)
    c_prog = re.sub(r'"key"', to_c_byte_array(key), c_prog)
    c_prog = re.sub(r'"flag_length"', str(len(flag_enc)), c_prog)

    open("main_compile.c", "w+", encoding="utf-8").write(c_prog)


if __name__ == "__main__":
    main()
