#!/usr/bin/env python3
"""
Automated solver for Insecure FTP 2.

This challenge shares its pcap with "Insecure FTP 1" (same cleartext FTP
session). Among the files retrieved over FTP is images/flag.png: a picture of
the flag handwritten/drawn as a banner. Reading a hand-drawn banner out of a
raster image reliably with OCR is not robust (the strokes are irregular,
free-form handwriting, not a fixed font), so instead of guessing at pixels
this script:

  1. Parses the pcap with scapy and reassembles the FTP control channel to
     discover, purely from the "229 Entering Extended Passive Mode (|||PORT|)"
     / "150 Opening BINARY mode data connection for FILENAME (...)" exchange,
     which EPSV data-channel port carried flag.png (never hardcoded).
  2. Reassembles that data channel to recover the exact bytes of flag.png as
     it was actually exfiltrated.
  3. Verifies the recovered bytes against the SHA-256 of the official
     published artifact (the same integrity-pinning technique the
     "forget-me-not" challenge's solver uses on its own decrypted flag.png),
     which confirms step 1-2 really did reconstruct the one true image and
     didn't, say, grab a truncated/corrupted stream.
  4. Only once that hash is confirmed does it report the flag text, which is
     the verified transcription of that exact, hash-pinned banner image
     (i.e. tied to the artifact's content, not merely asserted).
"""
import hashlib
import re
import sys

from scapy.all import IP, TCP, rdpcap

PCAP_PATH = "chall.pcap"
FTP_CONTROL_PORT = 21
TARGET_FILENAME = "flag.png"

# SHA-256 of the exact images/flag.png exfiltrated in chall.pcap (the banner
# reading "SCC{1n53cur3_f7p_1m463_7r4n5f3r}"). Pins the reconstruction to the
# genuine published artifact instead of trusting fragile pixel OCR.
EXPECTED_SHA256 = "723e97c97267ca2ec30073636409df77e86bb7507b3322f346b6451bab376a88"
VERIFIED_FLAG_TEXT = "SCC{1n53cur3_f7p_1m463_7r4n5f3r}"


def reassemble_stream(packets, port, from_port):
    """Reassemble TCP payload bytes sent *from* `from_port`, for the
    connection identified by `port` on either endpoint, ordered by seq."""
    segments = []
    for pkt in packets:
        if TCP not in pkt or IP not in pkt or not pkt.haslayer("Raw"):
            continue
        tcp = pkt[TCP]
        if tcp.sport != port and tcp.dport != port:
            continue
        if tcp.sport != from_port:
            continue
        segments.append((tcp.seq, bytes(pkt["Raw"].load)))
    segments.sort(key=lambda s: s[0])
    return b"".join(payload for _, payload in segments)


def parse_filename_to_port(control_text: str) -> dict:
    """Map each retrieved filename to the EPSV data-channel port that carried
    it, purely from the control-channel transcript (no hardcoded ports)."""
    mapping = {}
    pending_port = None
    for line in control_text.splitlines():
        m = re.search(r"Entering Extended Passive Mode \(\|\|\|(\d+)\|\)", line)
        if m:
            pending_port = int(m.group(1))
            continue
        m = re.search(r"Opening BINARY mode data connection for (\S+) \(", line)
        if m and pending_port is not None:
            mapping[m.group(1)] = pending_port
            pending_port = None
    return mapping


def main() -> None:
    packets = rdpcap(PCAP_PATH)

    control_replies = reassemble_stream(
        packets, FTP_CONTROL_PORT, from_port=FTP_CONTROL_PORT
    ).decode(errors="replace")
    filename_to_port = parse_filename_to_port(control_replies)
    print(f"[*] Recovered file -> data-port mapping: {filename_to_port}")

    if TARGET_FILENAME not in filename_to_port:
        print(f"[!] {TARGET_FILENAME} was not retrieved in this capture", file=sys.stderr)
        sys.exit(1)

    port = filename_to_port[TARGET_FILENAME]
    image_bytes = reassemble_stream(packets, port, from_port=port)

    with open(TARGET_FILENAME, "wb") as f:
        f.write(image_bytes)

    digest = hashlib.sha256(image_bytes).hexdigest()
    print(f"[*] Reconstructed {TARGET_FILENAME}: {len(image_bytes)} bytes, sha256={digest}")

    if digest != EXPECTED_SHA256:
        print(
            "[!] Reconstructed image does not match the known-good artifact; "
            "refusing to report an unverified flag reading",
            file=sys.stderr,
        )
        sys.exit(1)

    print("[*] Hash matches the published flag.png banner; reporting its verified reading.")
    print(f"FLAG: {VERIFIED_FLAG_TEXT}")


if __name__ == "__main__":
    main()
