#!/usr/bin/env python3
"""Solver for "The Intruder's Message".

The phishing email contains a VBScript attachment whose payload string is
built character-by-character via obfuscated arithmetic expressions such as:

    chr(-93615+CLng("&H16dfe"))
    chr(9381904/CLng("&H14737"))
    chr(CLng("&H6f59")-28389)

Evaluating every chr(...) term reconstructs the real VBScript source, which
in turn exfiltrates recon data to an attacker server together with a
hex-encoded, base64-encoded secret (decoded in-script by a `v3H` helper that
turns hex pairs back into characters). Decoding that same hex+base64 chain
recovers the flag.
"""
import base64
import email
import re
import sys
from email import policy


def decode_vbs_chr_obfuscation(vbs_source: str) -> str:
    """Evaluate every `chr(<arith expr involving CLng("&H...")>)` term."""

    def clng_to_int(match: "re.Match[str]") -> str:
        return str(int(match.group(1), 16))

    terms = re.findall(r'chr\(([^()]*(?:\([^()]*\)[^()]*)*)\)', vbs_source, re.IGNORECASE)
    chars = []
    for term in terms:
        expr = re.sub(r'CLng\("&H([0-9a-fA-F]+)"\)', clng_to_int, term, flags=re.IGNORECASE)
        chars.append(chr(int(eval(expr, {"__builtins__": {}}, {}))))
    return "".join(chars)


def extract_vbs_attachment(eml_path: str) -> str:
    with open(eml_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    for part in msg.walk():
        filename = part.get_filename() or ""
        if part.get_content_type() == "text/vbs" or filename.lower().endswith(".vbs"):
            return part.get_content()

    raise SystemExit("no .vbs attachment found in email")


def find_flag(decoded_vbs: str) -> str:
    # The decoded script embeds a long hex string literal that, once turned
    # back into bytes, is itself base64 for the final flag.
    for hex_candidate in re.findall(r'"([0-9a-fA-F]{20,})"', decoded_vbs):
        if len(hex_candidate) % 2 != 0:
            continue
        try:
            raw = bytes.fromhex(hex_candidate)
        except ValueError:
            continue
        try:
            b64_text = raw.decode("ascii")
        except UnicodeDecodeError:
            continue
        try:
            flag_bytes = base64.b64decode(b64_text, validate=True)
        except Exception:
            continue
        flag_match = re.search(rb"SCC\{[^}]*\}", flag_bytes)
        if flag_match:
            return flag_match.group(0).decode()

    raise SystemExit("flag not found after decoding VBS payload")


def main() -> int:
    eml_path = sys.argv[1] if len(sys.argv) > 1 else "email.eml"
    vbs_source = extract_vbs_attachment(eml_path)
    decoded_vbs = decode_vbs_chr_obfuscation(vbs_source)
    print("[*] Decoded VBScript:")
    print(decoded_vbs)
    flag = find_flag(decoded_vbs)
    print(f"FLAG: {flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
