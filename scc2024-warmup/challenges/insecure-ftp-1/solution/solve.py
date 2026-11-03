#!/usr/bin/env python3
"""
Automated solver for Insecure FTP 1.

The capture (chall.pcap, mounted next to this script) is a complete, cleartext
FTP session: the client authenticates as CyberHero/sajberheroj, then retrieves
several files (objective.txt, plans.txt, secret.txt, images/sajberheroj.png,
images/flag.png) over separate Extended Passive Mode (EPSV) data channels.

This script:
  1. Parses the pcap with scapy and reassembles the FTP *control* channel
     (TCP port 21) to recover the plaintext commands/responses, which is
     enough on its own to see the exfiltrated credentials.
  2. Walks that control-channel transcript to build a filename -> data-port
     mapping: every "229 Entering Extended Passive Mode (|||PORT|)" response
     is immediately followed (once a transfer starts) by a
     "150 Opening BINARY mode data connection for FILENAME (...)" response,
     so the two lines together tell us which TCP port carried which file.
  3. Reassembles the data-channel stream for secret.txt (whichever port that
     turned out to be - never hardcoded) and recovers its content.
  4. secret.txt contains a hex-encoded string labelled "Encoded Secret Flag";
     this script decodes that hex blob, which is the actual flag.
"""
import re
import sys

from scapy.all import IP, TCP, rdpcap

PCAP_PATH = "chall.pcap"
FTP_CONTROL_PORT = 21


def reassemble_stream(packets, port, from_port):
    """Reassemble the TCP payload bytes sent *from* `from_port` on either side
    of a connection that uses `port` as its other endpoint, ordered by TCP
    sequence number."""
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

    # Server->client replies (what we parse the EPSV/RETR bookkeeping from).
    control_replies = reassemble_stream(
        packets, FTP_CONTROL_PORT, from_port=FTP_CONTROL_PORT
    ).decode(errors="replace")
    # Client->server commands (USER/PASS/RETR/...): same control connection,
    # opposite direction, so "from_port" is whatever ephemeral port the
    # client used (identified as "not the control port").
    client_segments = [
        (pkt[TCP].seq, bytes(pkt["Raw"].load))
        for pkt in packets
        if TCP in pkt and pkt.haslayer("Raw") and pkt[TCP].dport == FTP_CONTROL_PORT
    ]
    client_segments.sort(key=lambda s: s[0])
    control_commands = b"".join(p for _, p in client_segments).decode(errors="replace")

    creds = re.search(r"USER (\S+)", control_commands)
    passw = re.search(r"PASS (\S+)", control_commands)
    if creds and passw:
        print(f"[*] Cleartext FTP credentials: {creds.group(1)}:{passw.group(1)}")

    filename_to_port = parse_filename_to_port(control_replies)
    print(f"[*] Recovered file -> data-port mapping: {filename_to_port}")

    if "secret.txt" not in filename_to_port:
        print("[!] secret.txt was not retrieved in this capture", file=sys.stderr)
        sys.exit(1)

    secret_port = filename_to_port["secret.txt"]
    secret_bytes = reassemble_stream(packets, secret_port, from_port=secret_port)
    secret_text = secret_bytes.decode(errors="replace")
    print("[*] secret.txt contents:")
    print(secret_text)

    m = re.search(r"Encoded Secret Flag: `([0-9a-fA-F]+)`", secret_text)
    if not m:
        print("[!] Could not find the encoded flag inside secret.txt", file=sys.stderr)
        sys.exit(1)

    flag = bytes.fromhex(m.group(1)).decode()
    print(f"FLAG: {flag}")


if __name__ == "__main__":
    main()
