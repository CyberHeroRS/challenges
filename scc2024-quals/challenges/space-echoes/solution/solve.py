#!/usr/bin/env python3
"""
Solver for "Space Echoes".

The capture contains a Flask login app served over plain HTTP. The TCP
streams carry the flag split into three parts:
  - Part 1: plaintext, hidden in an HTML comment on the login page.
  - Part 2: base64-encoded, hidden in an <input> placeholder attribute.
  - Part 3: plaintext, shown on the /home page after logging in.

This script reassembles every TCP stream found in capture.pcapng, scans the
reassembled text for the three "PART n : ..." markers (decoding part 2 from
base64), and concatenates them into the final SCC{...} flag.
"""
import base64
import re
import sys
from collections import defaultdict

from scapy.all import rdpcap, IP, TCP, Raw

PCAP_PATH = "capture.pcapng"

PART1_RE = re.compile(r"PART\s*1\s*:\s*([A-Za-z0-9_{]+)")
PART2_RE = re.compile(r"PART\s*2\s*:\s*([A-Za-z0-9_}]+)")
PART3_RE = re.compile(r"PART\s*3\s*:\s*([A-Za-z0-9_}]+)")
# Candidate base64 tokens that might carry the hidden/encoded part 2.
B64_CANDIDATE_RE = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")


def reassemble_streams(pcap_path):
    """Group TCP payload segments by connection+direction and reassemble
    each direction in sequence-number order, returning a list of decoded
    text blobs (one per direction per stream) to search through."""
    packets = rdpcap(pcap_path)

    # key: frozenset({(src_ip, src_port), (dst_ip, dst_port)})
    # value: dict direction -> {seq: payload}
    streams = defaultdict(lambda: defaultdict(dict))

    for pkt in packets:
        if IP in pkt and TCP in pkt and Raw in pkt:
            ip = pkt[IP]
            tcp = pkt[TCP]
            payload = bytes(tcp.payload)
            if not payload:
                continue
            src = (ip.src, tcp.sport)
            dst = (ip.dst, tcp.dport)
            key = frozenset((src, dst))
            streams[key][src][tcp.seq] = payload

    blobs = []
    for key, directions in streams.items():
        for direction, segments in directions.items():
            ordered = [segments[seq] for seq in sorted(segments.keys())]
            data = b"".join(ordered)
            blobs.append(data.decode("utf-8", errors="ignore"))
    return blobs


def find_part(blobs, pattern):
    for blob in blobs:
        match = pattern.search(blob)
        if match:
            return match.group(1)
    return None


def find_base64_part2(blobs):
    for blob in blobs:
        for candidate in B64_CANDIDATE_RE.findall(blob):
            try:
                # base64 requires padding to a multiple of 4.
                padded = candidate + "=" * (-len(candidate) % 4)
                decoded = base64.b64decode(padded, validate=False).decode(
                    "utf-8", errors="ignore"
                )
            except Exception:
                continue
            match = PART2_RE.search(decoded)
            if match:
                return match.group(1)
    return None


def main():
    blobs = reassemble_streams(PCAP_PATH)

    part1 = find_part(blobs, PART1_RE)
    part2 = find_base64_part2(blobs)
    part3 = find_part(blobs, PART3_RE)

    if not (part1 and part2 and part3):
        print(
            f"Failed to extract all parts (part1={part1!r}, part2={part2!r}, "
            f"part3={part3!r})",
            file=sys.stderr,
        )
        sys.exit(1)

    flag = part1 + part2 + part3
    print(f"Part 1: {part1}")
    print(f"Part 2 (base64 decoded): {part2}")
    print(f"Part 3: {part3}")
    print(f"FLAG: {flag}")


if __name__ == "__main__":
    main()
