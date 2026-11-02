#!/usr/bin/env python3
"""
Automated solver for Unseen Breach.

The capture shows an attacker fuzzing a "hash verification" web endpoint
(POST /api/verify {"hash": "<value>"}) that shells out to a hash-checker
script using the user-supplied value unsanitized. After some recon
(whoami, cat /etc/passwd, uname -a) the attacker finally injects a payload
that drops and runs a small python "exploit.py" which base64/RC4
exfiltrates files from ~/Desktop (PDFs and flag.txt) to a listener on
192.168.56.104:4444.

This script:
  1. Parses the pcap with scapy and reassembles each TCP stream.
  2. Locates the HTTP POST to /api/verify whose "hash" field contains the
     shell metacharacter " & " (the command injection) and prints the
     injected payload (including the embedded base64 python exfil stub).
  3. Locates the raw TCP stream to port 4444 used by the dropped exploit's
     send_file() routine: it sends b"file", then b"key" + 16-byte RC4 key,
     then the 256-byte, NUL-padded filename, then the RC4(key, data)
     ciphertext.
  4. RC4-decrypts the exfiltrated flag.txt content using the key that was
     itself captured in the same stream (nothing is hardcoded) and prints
     the recovered flag.
"""
import json
import sys

from scapy.all import rdpcap, TCP, Raw


def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)


def reassemble_streams(packets):
    """Group TCP payload bytes by (direction-agnostic) 4-tuple-normalized stream,
    keyed on the canonical (client, server) socket pair, split by direction."""
    streams = {}
    for pkt in packets:
        if TCP not in pkt or Raw not in pkt:
            continue
        ip = pkt.payload
        sport, dport = pkt[TCP].sport, pkt[TCP].dport
        src = (ip.src, sport)
        dst = (ip.dst, dport)
        # canonical key: sorted endpoints so both directions map to one stream
        key = tuple(sorted([src, dst]))
        streams.setdefault(key, {"to_dst": [], "to_src": []})
        # direction relative to the *first* observed packet's src
        first_src = streams[key].setdefault("_first_src", src)
        bucket = "to_dst" if src == first_src else "to_src"
        streams[key].setdefault(bucket, []).append(
            (pkt[TCP].seq, bytes(pkt[Raw].load))
        )
    reassembled = {}
    for key, data in streams.items():
        parts = {}
        for direction in ("to_dst", "to_src"):
            segs = sorted(data.get(direction, []), key=lambda s: s[0])
            parts[direction] = b"".join(payload for _, payload in segs)
        reassembled[key] = parts
    return reassembled


def find_injection_payload(packets):
    """Return every injected "hash" value that smuggles a shell metacharacter.
    The attacker iterates several payloads (pwd, whoami, cat /etc/passwd, ...)
    before the final one that drops and runs the exfiltration stub; we keep
    them all but report the final/longest one as *the* injection.

    HTTP headers and the JSON body land in separate TCP segments here, so we
    just scan every TCP payload that looks like a JSON object; the body is
    proper JSON (with backslash-escaped quotes inside the injected value
    itself), so json.loads correctly handles those escapes where a naive
    regex would stop at the first one."""
    payloads = []
    for pkt in packets:
        if TCP not in pkt or Raw not in pkt:
            continue
        load = bytes(pkt[Raw].load).strip()
        if not load.startswith(b"{"):
            continue
        try:
            obj = json.loads(load)
        except (ValueError, UnicodeDecodeError):
            continue
        value = obj.get("hash") if isinstance(obj, dict) else None
        if isinstance(value, str) and " & " in value:
            payloads.append(value)
    return payloads


def find_exfil_flag(packets):
    streams = reassemble_streams(packets)
    for (a, b), parts in streams.items():
        # the exfil channel connects to tcp/4444
        if a[1] != 4444 and b[1] != 4444:
            continue
        client_to_server = parts["to_dst"]
        if not client_to_server.startswith(b"file"):
            continue
        buf = client_to_server[len(b"file"):]
        if not buf.startswith(b"key"):
            continue
        buf = buf[len(b"key"):]
        key = buf[:16]
        buf = buf[16:]
        filename_raw = buf[:256]
        filename = filename_raw.rstrip(b"\x00").decode(errors="replace")
        ciphertext = buf[256:]
        if not ciphertext:
            continue
        plaintext = rc4(key, ciphertext)
        yield filename, key, plaintext


def main():
    pcap_path = "capture.pcapng"
    packets = rdpcap(pcap_path)

    payloads = find_injection_payload(packets)
    if payloads:
        print(f"[*] Found {len(payloads)} command-injection attempt(s) in POST /api/verify:")
        for p in payloads:
            print("    - " + p)
        final_payload = max(payloads, key=len)
        print("[*] Final (exfiltration) payload:")
        print("    " + final_payload)
    else:
        print("[!] Could not locate the injection payload", file=sys.stderr)

    found_flag = False
    for filename, key, plaintext in find_exfil_flag(packets):
        print(f"[*] Exfiltrated file: {filename!r} (RC4 key={key!r})")
        try:
            text = plaintext.decode().strip()
        except UnicodeDecodeError:
            text = None
        if text:
            print(f"    contents: {text}")
        if filename == "flag.txt" and text:
            print(f"FLAG: {text}")
            found_flag = True

    if not found_flag:
        print("[!] Did not recover flag.txt from the exfil stream", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
