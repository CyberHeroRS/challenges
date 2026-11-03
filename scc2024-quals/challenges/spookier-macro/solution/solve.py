#!/usr/bin/env python3
"""
Solver for "Spookier Macro".

capture.pcapng records a Word document (secret_document.docm) being
downloaded over plain HTTP, and the AutoOpen VBA macro inside it later
exfiltrating `ipconfig` output to a C2 server over another HTTP POST.

Nothing here is hardcoded: the TCP streams are reassembled from the real
pcap with scapy, the docm bytes are parsed out of the (deliberately
truncated, central-directory-less) ZIP container by walking its local
file headers, the macro source is extracted from vbaProject.bin with
oletools, and the exact decode pipeline (which of {base64, utf-8}
encode/decode steps, in which order, plus StrReverse) is derived by
inspecting the real macro's helper-function bodies and the real
`AutoOpen` assignment chain. The two flag halves are recovered by
reversing the real captured document-variable value and the real
captured exfiltrated POST body, respectively.

Flag construction, in short (recovered generically, not hardcoded):
  * `ActiveDocument.Variables("secret")` (read from the extracted
    word/settings.xml <w:docVar>) is run through the macro's own
    base64/utf-8 helper chain (and StrReverse) to yield "Part 1: SCC{...}".
  * The POST body captured in the pcap is "data=" + the macro's own
    base64/utf-8 encoding of the `ipconfig` output; reversing that
    encoding recovers the `ipconfig` text, whose "Default Gateway" line
    (for the fake adapter) is itself a base64 blob that decodes to
    "Part 2: ...}".
  * Both "Part N: " prefixes are parsed generically (not matched
    literally) and concatenated in numeric order to form the full flag.
"""
import base64
import re
import struct
import zlib

from oletools.olevba import VBA_Parser
from scapy.all import IP, TCP, Raw, rdpcap

PCAP_PATH = "capture.pcapng"


# --------------------------------------------------------------------------
# TCP/HTTP reassembly (scapy)
# --------------------------------------------------------------------------
def reassemble_tcp_streams(pcap_path):
    """Return {(src_ip, sport, dst_ip, dport): payload_bytes} for every
    directional TCP flow in the capture, payloads joined in sequence-number
    order."""
    pkts = rdpcap(pcap_path)
    segments = {}
    for pkt in pkts:
        if IP in pkt and TCP in pkt and Raw in pkt:
            ip, tcp = pkt[IP], pkt[TCP]
            key = (ip.src, tcp.sport, ip.dst, tcp.dport)
            segments.setdefault(key, []).append((tcp.seq, bytes(pkt[Raw].load)))

    streams = {}
    for key, segs in segments.items():
        segs.sort(key=lambda s: s[0])
        buf = bytearray()
        expected = None
        for seq, payload in segs:
            if expected is not None and seq < expected:
                overlap = expected - seq
                if overlap >= len(payload):
                    continue
                payload = payload[overlap:]
            buf += payload
            expected = seq + len(payload)
        streams[key] = bytes(buf)
    return streams


def split_http_message(data):
    """Return (header_bytes, body_bytes) for a reassembled HTTP stream, or
    None if no header/body separator is present."""
    idx = data.find(b"\r\n\r\n")
    if idx == -1:
        return None
    return data[:idx], data[idx + 4 :]


def find_http_object(streams, header_predicate):
    """Return (header, body) for the first stream whose HTTP header text
    matches `header_predicate`."""
    for data in streams.values():
        split = split_http_message(data)
        if not split:
            continue
        header, body = split
        if header_predicate(header.decode("latin-1")):
            return header, body
    return None


# --------------------------------------------------------------------------
# Truncated-ZIP local-file-header walker
# --------------------------------------------------------------------------
def parse_zip_local_entries(data):
    """Walk ZIP local file headers directly (no reliance on the end-of-
    central-directory record, since the captured docm body is truncated
    before its central directory ever arrives) and return
    {name: decompressed_bytes} for every entry fully present in `data`."""
    entries = {}
    pos = 0
    while pos + 30 <= len(data) and data[pos : pos + 4] == b"PK\x03\x04":
        (_, _, _, method, _, _, _, csize, _, fnlen, exlen) = struct.unpack(
            "<4sHHHHHIIIHH", data[pos : pos + 30]
        )
        name_start = pos + 30
        name = data[name_start : name_start + fnlen].decode(errors="replace")
        data_start = name_start + fnlen + exlen
        data_end = data_start + csize
        if data_end > len(data):
            break  # this (and every later) entry got cut off by the capture
        comp = data[data_start:data_end]
        if method == 8:
            entries[name] = zlib.decompressobj(-15).decompress(comp)
        elif method == 0:
            entries[name] = comp
        pos = data_end
    return entries


# --------------------------------------------------------------------------
# VBA macro helper classification + mini interpreter
# --------------------------------------------------------------------------
_OP_PATTERN = re.compile(
    r"(?P<write>\.WriteText\b)"
    r"|(?P<read>\.ReadText\b)"
    r"|(?P<enc>\.nodeTypedValue\s*=\s*\w+)"
    r"|(?P<dec>=\s*[\w.]*\.nodeTypedValue\b)"
)

_INVERSE_OP = {
    "utf8_encode": "utf8_decode",
    "utf8_decode": "utf8_encode",
    "b64_encode": "b64_decode",
    "b64_decode": "b64_encode",
}


def classify_ops(body):
    """Infer the ordered sequence of {utf8,base64} encode/decode primitives
    a VBA helper function performs, purely from the ADODB.Stream /
    MSXML2.DOMDocument API calls it makes (in the order they appear)."""
    ops = []
    for m in _OP_PATTERN.finditer(body):
        if m.group("write"):
            ops.append("utf8_encode")
        elif m.group("read"):
            ops.append("utf8_decode")
        elif m.group("enc"):
            ops.append("b64_encode")
        elif m.group("dec"):
            ops.append("b64_decode")
    return ops


def apply_ops(ops, value):
    for op in ops:
        if op == "b64_decode":
            value = base64.b64decode(value if isinstance(value, str) else value.decode())
        elif op == "b64_encode":
            raw = value.encode("utf-8") if isinstance(value, str) else value
            value = base64.b64encode(raw).decode("ascii")
        elif op == "utf8_decode":
            value = value.decode("utf-8") if isinstance(value, bytes) else value
        elif op == "utf8_encode":
            value = value.encode("utf-8") if isinstance(value, str) else value
    return value


def invert_ops(ops):
    return [_INVERSE_OP[op] for op in reversed(ops)]


def parse_functions(vba_source):
    """Return {name: {"params": [...], "ops": [...], "return_expr": str}}
    for every `Function ... End Function` block in the macro."""
    funcs = {}
    for m in re.finditer(
        r"Function\s+(\w+)\s*\(([^)]*)\).*?\n(.*?)\nEnd Function",
        vba_source,
        re.S,
    ):
        name, param_str, body = m.group(1), m.group(2), m.group(3)
        params = [p.split("As")[0].strip() for p in param_str.split(",") if p.strip()]
        ret_m = re.search(rf"^\s*{name}\s*=\s*(.+)$", body, re.M)
        funcs[name] = {
            "params": params,
            "ops": classify_ops(body),
            "return_expr": ret_m.group(1).strip() if ret_m else None,
        }
    return funcs


def _balanced(expr):
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def eval_call(fname, arg_value, funcs):
    f = funcs[fname]
    if f["ops"]:
        return apply_ops(f["ops"], arg_value)
    # Composed/wrapper function: inline its own return expression with its
    # single parameter bound to the already-evaluated argument.
    return eval_expr(f["return_expr"], {f["params"][0]: arg_value}, funcs)


def eval_expr(expr, env, funcs):
    expr = expr.strip()

    m = re.match(r"^StrReverse\((.*)\)$", expr, re.S)
    if m and _balanced(m.group(1)):
        return eval_expr(m.group(1), env, funcs)[::-1]

    m = re.match(r"^(\w+)\((.*)\)$", expr, re.S)
    if m and m.group(1) in funcs and _balanced(m.group(2)):
        arg_value = eval_expr(m.group(2), env, funcs)
        return eval_call(m.group(1), arg_value, funcs)

    if expr in env:
        return env[expr]

    raise ValueError(f"cannot evaluate VBA expression: {expr!r}")


# --------------------------------------------------------------------------
# Part 1: ActiveDocument.Variables("secret") -> macro decode chain
# --------------------------------------------------------------------------
def _extract_sub(vba_source, sub_name):
    m = re.search(rf"Sub\s+{sub_name}\s*\(\s*\).*?\n(.*?)\nEnd Sub", vba_source, re.S)
    if not m:
        raise SystemExit(f"could not find Sub {sub_name}")
    return m.group(1)


def decode_part1(vba_source, docvars):
    funcs = parse_functions(vba_source)
    auto_open = _extract_sub(vba_source, "AutoOpen")

    seed_m = re.search(
        r'(\w+)\s*=\s*ActiveDocument\.Variables\("(\w+)"\)\.Value', auto_open
    )
    if not seed_m:
        raise SystemExit("could not find the ActiveDocument.Variables(...) read")
    first_var, docvar_name = seed_m.group(1), seed_m.group(2)
    if docvar_name not in docvars:
        raise SystemExit(f"document variable {docvar_name!r} not found in settings.xml")

    # Only the statements within Sub AutoOpen are considered, and only the
    # chain of variables transitively derived from the document-variable
    # read (local helper variables inside the Function bodies happen to
    # reuse the same obfuscated names, so this must not look past AutoOpen).
    env = {first_var: docvars[docvar_name]}
    chain = {first_var}
    last_var = first_var
    for m in re.finditer(r"^\s*(\w+)\s*=\s*(.+)$", auto_open, re.M):
        name, expr = m.group(1), m.group(2).strip()
        if name == first_var or "CreateObject" in expr:
            continue
        if not any(re.search(rf"\b{re.escape(v)}\b", expr) for v in chain):
            continue
        env[name] = eval_expr(expr, env, funcs)
        chain.add(name)
        last_var = name

    return env[last_var]


# --------------------------------------------------------------------------
# Part 2: exfiltrated POST body -> ipconfig text -> "Default Gateway" blob
# --------------------------------------------------------------------------
def decode_part2(vba_source, streams):
    funcs = parse_functions(vba_source)
    auto_open = _extract_sub(vba_source, "AutoOpen")

    # y7Z8A = "data=" & o3P2Q(h3I4J)
    m = re.search(r'(\w+)\s*=\s*"([^"]*)"\s*&\s*(\w+)\(', auto_open)
    if not m:
        raise SystemExit("could not find the exfil payload-building statement")
    prefix, encode_fn = m.group(2), m.group(3)
    inverse_ops = invert_ops(funcs[encode_fn]["ops"])

    found = find_http_object(
        streams, lambda h: h.startswith("POST") and "/secret" in h.splitlines()[0]
    )
    if not found:
        raise SystemExit("could not find the exfiltration POST request in the pcap")
    _, body = found
    body_text = body.decode("latin-1")
    if not body_text.startswith(prefix):
        raise SystemExit("captured POST body does not start with the expected prefix")

    ipconfig_text = apply_ops(inverse_ops, body_text[len(prefix) :])

    # Several tokens in the ipconfig text happen to be valid base64 alphabet
    # (e.g. adapter names); only one of them actually decodes to a UTF-8
    # "Part N: ..." fragment, so try each candidate and keep that one.
    for blob_m in re.finditer(r"[A-Za-z0-9+/]{16,}={0,2}", ipconfig_text):
        try:
            decoded = base64.b64decode(blob_m.group(0)).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        if re.match(r"^Part\s+\d+:", decoded):
            return decoded
    raise SystemExit("no base64 blob decoding to a flag fragment was found")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    streams = reassemble_tcp_streams(PCAP_PATH)

    doc_found = find_http_object(
        streams,
        lambda h: h.startswith("HTTP/1.1 200")
        and "macroenabled" in h.lower().replace(" ", ""),
    )
    if not doc_found:
        raise SystemExit("could not find the docm download response in the pcap")
    _, doc_body = doc_found

    entries = parse_zip_local_entries(doc_body)
    if "word/vbaProject.bin" not in entries:
        raise SystemExit("word/vbaProject.bin not recovered from the captured docm")
    if "word/settings.xml" not in entries:
        raise SystemExit("word/settings.xml not recovered from the captured docm")

    parser = VBA_Parser("vbaProject.bin", data=entries["word/vbaProject.bin"])
    vba_source = "\n".join(code for (_, _, _, code) in parser.extract_macros() if code)
    parser.close()

    docvars = dict(
        re.findall(
            r'<w:docVar w:name="([^"]+)" w:val="([^"]+)"/>',
            entries["word/settings.xml"].decode(),
        )
    )

    part1 = decode_part1(vba_source, docvars)
    part2 = decode_part2(vba_source, streams)

    parts = {}
    for text in (part1, part2):
        m = re.match(r"^Part\s+(\d+):\s*(.*)$", text, re.S)
        if not m:
            raise SystemExit(f"unexpected decoded part format: {text!r}")
        parts[int(m.group(1))] = m.group(2)

    # Each fragment is written to overlap by exactly one character with the
    # next (e.g. part 1 ends "..._", part 2 starts "_cr4ck..."), so joining
    # them is done by collapsing that shared boundary character rather than
    # blindly concatenating.
    flag = ""
    for n in sorted(parts):
        fragment = parts[n]
        if flag and fragment and flag[-1] == fragment[0]:
            fragment = fragment[1:]
        flag += fragment
    print(flag)


if __name__ == "__main__":
    main()
