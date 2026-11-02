#!/bin/sh
# Solver for "johnny": crack the password-protected ZIP with the real
# rockyou.txt wordlist (same technique the challenge always intended),
# extract flag.txt, and let the Dockerfile's CMD verify it against the
# flag injected by the test runner.
set -eu

ZIP="johnny.zip"
WORDLIST="/usr/share/wordlists/rockyou.txt"

echo "[*] Cracking ZIP password with fcrackzip + rockyou.txt..."
FCRACK_OUT="$(fcrackzip -u -D -p "$WORDLIST" "$ZIP")"
echo "$FCRACK_OUT"

PASSWORD="$(printf '%s\n' "$FCRACK_OUT" | sed -n 's/.*PASSWORD FOUND!!!!: pw == //p')"

if [ -z "$PASSWORD" ]; then
    echo "[!] Failed to crack the ZIP password" >&2
    exit 1
fi

echo "[*] Cracked password: $PASSWORD"
echo "[*] Extracting flag.txt..."
unzip -P "$PASSWORD" -o "$ZIP" flag.txt -d extracted

echo "[*] Flag:"
cat extracted/flag.txt
