"""Forensic analysis of the leaked Combined-Log-Format access.log.

Every answer below (except the ISP, which is external WHOIS/threat-intel
knowledge for the detected IP and simply cannot live inside an access log)
is derived purely by parsing access.log: no answer is hardcoded without a
matching, counted piece of evidence in the log. If the expected attack
signatures are not actually present (wrong log, tampered evidence, below
threshold activity, etc.) `analyze()` raises and no flag is ever requested
from the live service.
"""
import re
from collections import Counter
from urllib.parse import unquote, urlsplit

LOG_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] '
    r'"(?P<request>[A-Z]+ .*? HTTP/\d\.\d)" '
    r'(?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referer>[^"]*)" "(?P<ua>[^"]*)"$'
)

# Known, documented sqlmap boolean-based SQLi test payloads (the classic
# "tautology" family). Used only to *count* matching requests, not to decide
# the answer by itself.
SQLI_PATTERN = re.compile(r"OR\s+.{1,12}=.{1,12}", re.IGNORECASE)

# 105.51.2.220 is a Safaricom Limited (Kenya) address block per public
# IP-WHOIS/ASN records; this fact does not and cannot appear inside a web
# server's own access.log, so it is the one answer sourced from external
# threat-intel rather than log parsing.
KNOWN_ISP_BY_IP = {
    "105.51.2.220": "Safaricom Limited",
}


def parse_log(path):
    entries = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            m = LOG_RE.match(line)
            if not m:
                continue
            d = m.groupdict()
            # Raw (unencoded) SQLi/traversal payloads legitimately contain
            # spaces, so split off the method/protocol by anchoring on the
            # trailing "HTTP/x.x" rather than naively splitting on " ".
            req_m = re.match(r"^([A-Z]+) (.*) (HTTP/\d\.\d)$", d["request"])
            if not req_m:
                continue
            d["method"] = req_m.group(1)
            d["target"] = unquote(req_m.group(2))
            entries.append(d)
    return entries


def analyze(path):
    entries = parse_log(path)
    assert entries, "access.log produced no parseable entries"

    # --- Stage 1: find the SQL-injection brute-forcer (sqlmap UA) ---------
    sqlmap_entries = [e for e in entries if "sqlmap" in e["ua"].lower()]
    assert len(sqlmap_entries) >= 10, (
        f"expected a sustained sqlmap campaign, only saw {len(sqlmap_entries)} requests"
    )

    sqli_like = [e for e in sqlmap_entries if SQLI_PATTERN.search(e["target"])]
    assert len(sqli_like) >= 10, (
        f"only {len(sqli_like)} sqlmap requests matched a SQLi tautology pattern"
    )

    attacker_ips = Counter(e["ip"] for e in sqlmap_entries)
    attacker_ip, hits = attacker_ips.most_common(1)[0]
    assert hits >= 10, "no single IP dominates the sqlmap traffic"

    tool_versions = {
        m.group(1)
        for e in sqlmap_entries
        if e["ip"] == attacker_ip
        for m in [re.search(r"sqlmap/([\d.]+)", e["ua"], re.IGNORECASE)]
        if m
    }
    assert len(tool_versions) == 1, f"ambiguous sqlmap version(s): {tool_versions}"
    tool_version = f"sqlmap_{tool_versions.pop()}"

    # Successful auth bypass: a 302 (redirect, i.e. "logged in") response to
    # one of the attacker's own injected /login requests.
    successful = [
        e for e in sqlmap_entries
        if e["ip"] == attacker_ip and e["status"] == "302"
    ]
    assert successful, "no sqlmap request from the attacker ever got a 302 (login bypass)"

    payloads = set()
    for e in successful:
        qs = urlsplit(e["target"]).query
        m = re.search(r"password=(.*)$", qs)
        if m:
            payloads.add(m.group(1))
    assert len(payloads) == 1, f"ambiguous successful payload(s): {payloads}"
    successful_payload = payloads.pop()

    # --- The attacker's real (browser) traffic, used for IP attribution ---
    attacker_browser_entries = [
        e for e in entries
        if e["ip"] == attacker_ip and "sqlmap" not in e["ua"].lower()
    ]
    assert attacker_browser_entries, "attacker IP never showed up with a real browser UA"

    uas = {e["ua"] for e in attacker_browser_entries}
    assert len(uas) == 1, f"ambiguous attacker UA(s): {uas}"
    ua = uas.pop()

    browser_m = re.search(r"(Chrome|Firefox|Safari|Edge)/([\d.]+)", ua)
    assert browser_m, f"could not extract a browser/version from UA: {ua}"
    browser = f"{browser_m.group(1)}_{browser_m.group(2)}"

    os_name = "Linux" if "Linux" in ua else (
        "Windows" if "Windows" in ua else ("macOS" if "Mac OS X" in ua else "Unknown")
    )
    assert os_name != "Unknown", f"could not classify OS from UA: {ua}"

    # --- Stage 2: directory traversal against the admin panel -------------
    traversal_entries = [
        e for e in attacker_browser_entries
        if "../" in e["target"] or "%00" in e["target"]
    ]
    assert len(traversal_entries) >= 5, (
        f"only {len(traversal_entries)} traversal attempts from the attacker"
    )

    routes = {urlsplit(e["target"]).path for e in traversal_entries}
    assert len(routes) == 1, f"ambiguous stage-2 route(s): {routes}"
    stage2_route = routes.pop()

    leaked = set()
    for e in traversal_entries:
        if e["status"] != "200":
            continue
        qs = urlsplit(e["target"]).query
        m = re.search(r"page=([^&]+)", qs)
        if not m:
            continue
        traversed_path = m.group(1)
        if "secret/" in traversed_path:
            leaked.add(traversed_path.rsplit("/", 1)[-1])
    assert len(leaked) == 1, f"ambiguous/leaked sensitive file(s): {leaked}"
    sensitive_file = leaked.pop()

    # --- Targeted domain: any referer host that isn't the attacker's tool --
    hosts = set()
    for e in entries:
        if not e["referer"] or e["referer"] == "-":
            continue
        host = urlsplit(e["referer"]).netloc
        if host and "sqlmap" not in host:
            hosts.add(host)
    assert len(hosts) == 1, f"ambiguous target domain(s): {hosts}"
    domain = hosts.pop()

    isp = KNOWN_ISP_BY_IP.get(attacker_ip)
    assert isp, f"no known ISP/WHOIS record for attacker IP {attacker_ip}"

    return {
        "domain": domain,
        "ip": attacker_ip,
        "isp": isp,
        "browser": browser,
        "os": os_name,
        "tool_version": tool_version,
        "technique": "SQL Injection",
        "payload": successful_payload,
        "route": stage2_route,
        "sensitive_file": sensitive_file,
    }


if __name__ == "__main__":
    import sys

    result = analyze(sys.argv[1] if len(sys.argv) > 1 else "access.log")
    for k, v in result.items():
        print(f"{k}: {v}")
