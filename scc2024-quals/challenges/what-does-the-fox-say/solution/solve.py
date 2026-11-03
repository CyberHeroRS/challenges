#!/usr/bin/env python3
"""Automated solver for "What Does The Fox Say?".

The challenge ships a Firefox profile (browser forensics zip) and runs a
netcat quiz service that only reveals the flag once all eight questions
about the captured browsing session are answered correctly. This script
derives every answer straight from the forensic artifacts (places.sqlite,
formhistory.sqlite, logins.json + key4.db) instead of hardcoding them, then
plays the quiz over the wire to recover the real flag.
"""
import base64
import configparser
import ctypes
import ctypes.util
import json
import os
import re
import socket
import sqlite3
import sys
import zipfile
from urllib.parse import urlparse

ZIP_PATH = "forensics_what_does_the_fox_say.zip"
WORKDIR = "extracted"

SEARCH_ENGINE_HOSTS = {
    "google.com",
    "www.google.com",
    "bing.com",
    "www.bing.com",
    "duckduckgo.com",
    "www.duckduckgo.com",
    "search.yahoo.com",
}
BROWSER_DEFAULT_HOSTS = {
    "www.mozilla.org",
    "mozilla.org",
    "support.mozilla.org",
}


def extract_zip():
    if not os.path.isdir(WORKDIR):
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(WORKDIR)


def find_default_profile_dir():
    """Resolve the default profile path the same way Firefox does: via
    installs.ini (falls back to profiles.ini) under the Firefox app dir."""
    firefox_dir = os.path.join(WORKDIR, "Firefox")
    for ini_name in ("installs.ini", "profiles.ini"):
        ini_path = os.path.join(firefox_dir, ini_name)
        if not os.path.isfile(ini_path):
            continue
        config = configparser.ConfigParser()
        config.read(ini_path)
        for section in config.sections():
            if config.has_option(section, "Default"):
                rel = config.get(section, "Default")
                candidate = os.path.join(firefox_dir, rel)
                if os.path.isfile(os.path.join(candidate, "places.sqlite")):
                    return candidate
    # Fallback: pick whichever profile directory actually has places.sqlite.
    profiles_root = os.path.join(firefox_dir, "Profiles")
    for name in os.listdir(profiles_root):
        candidate = os.path.join(profiles_root, name)
        if os.path.isfile(os.path.join(candidate, "places.sqlite")):
            return candidate
    raise RuntimeError("could not locate a Firefox profile with places.sqlite")


def site_label(url):
    netloc = urlparse(url).netloc
    netloc = netloc.split("@")[-1].split(":")[0]
    if netloc.startswith("www."):
        netloc = netloc[4:]
    label = netloc.split(".")[0]
    return label.capitalize()


def is_ipv4_host(netloc):
    host = netloc.split("@")[-1].split(":")[0]
    return re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host) is not None


def query_answers(profile_dir):
    places_db = os.path.join(profile_dir, "places.sqlite")
    formhistory_db = os.path.join(profile_dir, "formhistory.sqlite")

    conn = sqlite3.connect(f"file:{places_db}?immutable=1", uri=True)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.visit_date, p.url, p.title, p.visit_count
        FROM moz_historyvisits v
        JOIN moz_places p ON v.place_id = p.id
        ORDER BY v.visit_date ASC
        """
    )
    rows = cur.fetchall()

    # 1) First "real" website visited: earliest visit whose host isn't the
    # browser's own default pages or a search engine redirect/results page.
    first_site_url = None
    for _, url, _, _ in rows:
        netloc = urlparse(url).netloc
        if netloc in BROWSER_DEFAULT_HOSTS or netloc in SEARCH_ENGINE_HOSTS:
            continue
        first_site_url = url
        break
    first_site_name = site_label(first_site_url)
    first_site_domain = urlparse(first_site_url).netloc

    # 2) First subreddit URL visited: earliest visit under that same domain
    # with a non-root path (i.e. an actual subreddit, not the homepage).
    first_subreddit_url = None
    for _, url, _, _ in rows:
        parsed = urlparse(url)
        if parsed.netloc == first_site_domain and parsed.path not in ("", "/"):
            first_subreddit_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            break

    # 3) The "strange" URL: a plain IPv4 host visited directly.
    strange_url = None
    strange_title = None
    strange_count = None
    for _, url, title, visit_count in rows:
        parsed = urlparse(url)
        if is_ipv4_host(parsed.netloc) and parsed.path in ("", "/"):
            strange_url = f"{parsed.scheme}://{parsed.netloc}/"
            strange_title = title
            strange_count = visit_count
            break

    # 6) Band name: derive from a YouTube "<Artist> - Topic - YouTube" title,
    # which is YouTube's auto-generated artist channel title.
    band_name = None
    for _, url, title, _ in rows:
        if "youtube.com/channel" in url and title and " - Topic - YouTube" in title:
            band_name = title.split(" - Topic - YouTube")[0].strip()
            break
    conn.close()

    # 7) Search term used for the band's concert, from the search bar history.
    search_term = None
    if band_name and os.path.isfile(formhistory_db):
        fh_conn = sqlite3.connect(f"file:{formhistory_db}?immutable=1", uri=True)
        fh_cur = fh_conn.cursor()
        fh_cur.execute(
            "SELECT value FROM moz_formhistory WHERE fieldname = 'searchbar-history'"
        )
        band_words = band_name.lower().split()
        for (value,) in fh_cur.fetchall():
            lowered = value.lower()
            if all(word in lowered for word in band_words) and "concert" in lowered:
                search_term = value
                break
        fh_conn.close()

    return {
        "first_site_name": first_site_name,
        "first_subreddit_url": first_subreddit_url,
        "strange_url": strange_url,
        "strange_title": strange_title,
        "strange_count": str(strange_count),
        "band_name": band_name,
        "search_term": search_term,
    }


# --- NSS-based decryption of the saved Firefox login (logins.json + key4.db) ---


class SECItem(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint),
        ("data", ctypes.c_char_p),
        ("len", ctypes.c_uint),
    ]


def decrypt_credentials(profile_dir):
    logins_path = os.path.join(profile_dir, "logins.json")
    with open(logins_path) as f:
        logins = json.load(f)
    login = logins["logins"][0]

    nss = ctypes.CDLL(ctypes.util.find_library("nss3") or "libnss3.so")
    nss.NSS_Init.argtypes = [ctypes.c_char_p]
    nss.NSS_Init.restype = ctypes.c_int
    nss.NSS_Shutdown.restype = ctypes.c_int
    nss.PK11_GetInternalKeySlot.restype = ctypes.c_void_p
    nss.PK11_Authenticate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    nss.PK11_Authenticate.restype = ctypes.c_int
    nss.PK11SDR_Decrypt.argtypes = [
        ctypes.POINTER(SECItem),
        ctypes.POINTER(SECItem),
        ctypes.c_void_p,
    ]
    nss.PK11SDR_Decrypt.restype = ctypes.c_int

    rc = nss.NSS_Init(f"sql:{profile_dir}".encode())
    if rc != 0:
        raise RuntimeError(f"NSS_Init failed rc={rc}")
    try:
        slot = nss.PK11_GetInternalKeySlot()
        rc = nss.PK11_Authenticate(slot, 1, None)
        if rc != 0:
            raise RuntimeError(f"PK11_Authenticate failed rc={rc}")

        def decrypt(b64data):
            raw = base64.b64decode(b64data)
            inp = SECItem(0, raw, len(raw))
            outp = SECItem(0, None, 0)
            rc = nss.PK11SDR_Decrypt(ctypes.byref(inp), ctypes.byref(outp), None)
            if rc != 0:
                raise RuntimeError(f"PK11SDR_Decrypt failed rc={rc}")
            return ctypes.string_at(outp.data, outp.len).decode()

        username = decrypt(login["encryptedUsername"])
        password = decrypt(login["encryptedPassword"])
    finally:
        nss.NSS_Shutdown()
    return username, password


def recvuntil(sock, marker=b"Answer: ", timeout=15):
    sock.settimeout(timeout)
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def main():
    extract_zip()
    profile_dir = find_default_profile_dir()
    answers_data = query_answers(profile_dir)
    username, password = decrypt_credentials(profile_dir)

    for key, value in {**answers_data, "username": username, "password": password}.items():
        print(f"[+] {key} = {value}", file=sys.stderr)

    answers = [
        answers_data["first_site_name"],
        answers_data["first_subreddit_url"],
        answers_data["strange_url"],
        answers_data["strange_title"],
        answers_data["strange_count"],
        answers_data["band_name"],
        answers_data["search_term"],
        f"{username}:{password}",
    ]

    host = os.environ["SERVICE_APP_MAIN_HOST"]
    port = int(os.environ["SERVICE_APP_MAIN_PORT"])

    sock = socket.create_connection((host, port), timeout=15)
    transcript = b""
    for answer in answers:
        chunk = recvuntil(sock, b"Answer: ")
        transcript += chunk
        sock.sendall(answer.encode() + b"\n")
    sock.settimeout(15)
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        transcript += chunk
    sock.close()

    output = transcript.decode(errors="replace")
    print(output)
    if "Congratulations" not in output:
        print("[-] did not reach the congratulations/flag message", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
