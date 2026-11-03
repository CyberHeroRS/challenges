#!/usr/bin/env python3
"""
Solver for the "serial" rev challenge.

Static analysis of public/serial.exe (x86-64 PE, console subsystem, no CRT --
entry point calls GetCommandLineW/CommandLineToArgvW/StrToIntW/wsprintfW/
WriteConsoleW directly, imports only KERNEL32/USER32/SHELL32/SHLWAPI, see
`objdump -p`) shows the following validation algorithm for argv[1] ("the
serial"), a string of the form "AAAA-BBBB-CCCC-DDDD" (len >= 19, dashes
required at char indices 4, 9 and 14):

    p1 = StrToIntW(serial)          # leading digits of group "AAAA"
    p2 = StrToIntW(serial + 5)      # leading digits of group "BBBB"
    p3 = StrToIntW(serial + 10)     # leading digits of group "CCCC"
    p4 = StrToIntW(serial + 15)     # leading digits of group "DDDD"

    ok  = (p1 % 400 == 0)                      # magic-multiply div-by-400 check
    ok &= (p1 - p2 == 0x1644)                   # == 5700
    ok &= (p2 * p3 == 0x11170)                  # == 70000
    ok &= (p4 == (p1 + p2 + p3) & 0x2710)       # bitwise AND with 10000

If (and only if) all four hold, the binary XOR-decrypts a 42-byte buffer
embedded in .data (RVA 0x3010, right after ImageBase) using the serial's own
ASCII bytes as a repeating-cyclic XOR key (period == len(serial)); the first
3 bytes of that buffer are always "SCC" verbatim, bytes [3:41] are XORed with
serial[k % len(serial)] for k = 0..37, and the decrypted result is printed as
"Congrats, here's your flag: %hs\n". Any failed check instead prints
"Try again\n".

Because "crack the serial" means deriving a *valid* key via the real check
logic (not guessing a fixed string), we solve the four equations above
algebraically for (p1, p2, p3, p4), then -- for every arithmetically valid
candidate -- use the exact XOR-decrypt logic above (sourced from the real
ciphertext bytes read directly out of the PE image) to see which candidate
actually decrypts to a well-formed "SCC{...}" flag. We additionally attempt a
genuine dynamic run of the binary itself under Wine (through a pty, since
this console app's WriteConsoleW silently no-ops when stdout is a plain pipe)
and prefer whatever it prints, falling back to the static reproduction when
Wine is unavailable or does not cooperate.
"""
import os
import pty
import re
import select
import shutil
import subprocess
import sys
import time

EXE_NAME = "serial.exe"
FLAG_RE = re.compile(r"SCC\{[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\}")

# Constants pulled straight out of the disassembly (see module docstring).
DIV_MOD = 400
DIFF_12 = 0x1644   # 5700
PROD_23 = 0x11170  # 70000
SUM_MASK = 0x2710  # 10000


def solve_candidates():
    """Algebraically reverse the four arithmetic checks for every valid
    (p1, p2, p3, p4) quadruple representable as 4-digit decimal groups."""
    candidates = []
    for k in range(0, 10000 // DIV_MOD + 1):
        p1 = DIV_MOD * k
        if p1 > 9999:
            break
        p2 = p1 - DIFF_12
        if p2 <= 0 or p2 > 9999:
            continue
        if PROD_23 % p2 != 0:
            continue
        p3 = PROD_23 // p2
        if p3 < 0 or p3 > 9999:
            continue
        p4 = (p1 + p2 + p3) & SUM_MASK
        if p4 > 9999:
            continue
        candidates.append((p1, p2, p3, p4))
    return candidates


def serial_string(quad):
    p1, p2, p3, p4 = quad
    return f"{p1:04d}-{p2:04d}-{p3:04d}-{p4:04d}"


def read_ciphertext(exe_path: str) -> bytes:
    """Read the real 42-byte XOR-encrypted buffer straight out of the PE
    image (RVA 0x3010, directly past ImageBase in .data), instead of
    hardcoding its bytes."""
    import pefile

    pe = pefile.PE(exe_path)
    image = pe.get_memory_mapped_image()
    rva = 0x3010
    return image[rva:rva + 42]


def decrypt_with_key(ciphertext: bytes, serial: str) -> str:
    """Exact re-implementation of the binary's own XOR-decrypt loop:
    first 3 bytes are plaintext "SCC", bytes [3:41] get XORed with the
    serial's own ASCII bytes cycled with period len(serial)."""
    n = len(serial)
    out = bytearray(ciphertext[:3])  # "SCC", never touched by the loop
    for k in range(38):
        out.append(ciphertext[3 + k] ^ ord(serial[k % n]))
    return out.decode("latin1")


def run_under_pty(cmd, env, cwd, timeout=25) -> str:
    """Run `cmd` with its stdio attached to a real pty. Needed because this
    console app's WriteConsoleW call silently does nothing when stdout is a
    plain (non-console) pipe/file, which is exactly what Docker/subprocess
    give it by default."""
    master, slave = pty.openpty()
    proc = subprocess.Popen(cmd, stdin=slave, stdout=slave, stderr=slave,
                             env=env, cwd=cwd, start_new_session=True)
    os.close(slave)
    output = bytearray()
    deadline = time.time() + timeout
    try:
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            ready, _, _ = select.select([master], [], [], min(remaining, 1.0))
            if master in ready:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
            if proc.poll() is not None:
                while True:
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if master not in ready:
                        break
                    try:
                        chunk = os.read(master, 4096)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
                break
    finally:
        os.close(master)
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return output.decode("utf-8", errors="replace")


def try_wine(exe_path: str, workdir: str, candidates) -> str | None:
    """Attempt genuine dynamic execution of the real binary under Wine for
    each algebraically-derived candidate serial, returning the flag text the
    binary itself printed for whichever candidate it actually accepts."""
    wine_bin = shutil.which("wine") or shutil.which("wine64")
    if wine_bin is None:
        return None
    local_exe = os.path.join(workdir, EXE_NAME)
    shutil.copyfile(exe_path, local_exe)

    prefix = os.path.join(workdir, ".wine")
    env = os.environ.copy()
    env["WINEPREFIX"] = prefix
    env["WINEDEBUG"] = "-all"
    env["WINEARCH"] = "win64"
    tmp = os.path.join(workdir, "winetmp")
    os.makedirs(tmp, exist_ok=True)
    env["TMP"] = tmp
    env["TEMP"] = tmp

    try:
        subprocess.run([wine_bin, "wineboot", "--init"], env=env, cwd=workdir,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    except Exception as exc:  # noqa: BLE001 - best-effort dynamic attempt
        print(f"[wine] wineboot failed: {exc!r}")
        return None

    for quad in candidates:
        serial = serial_string(quad)
        try:
            out = run_under_pty([wine_bin, EXE_NAME, serial], env, workdir, timeout=25)
        except Exception as exc:  # noqa: BLE001 - best-effort dynamic attempt
            print(f"[wine] run raised {exc!r} for serial {serial}")
            continue
        match = FLAG_RE.search(out)
        if "Congrats" in out and match:
            print(f"[wine] genuine run accepted serial {serial!r}: {out.strip()!r}")
            return match.group(0)
        print(f"[wine] serial {serial!r} -> {out.strip()!r}")
    return None


def main() -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, EXE_NAME)

    candidates = solve_candidates()
    assert candidates, "no candidate serial satisfied the real arithmetic checks"
    print(f"[+] {len(candidates)} candidate serial(s) satisfy p1%400==0, p1-p2==5700, "
          f"p2*p3==70000, p4==(p1+p2+p3)&10000:")
    for quad in candidates:
        print(f"    {serial_string(quad)}")

    workdir = os.path.join(os.getcwd(), "serial-run")
    os.makedirs(workdir, exist_ok=True)

    flag = try_wine(exe_path, workdir, candidates)

    if flag is None:
        print("[+] falling back to static reproduction of the verified XOR-decrypt logic")
        ciphertext = read_ciphertext(exe_path)
        for quad in candidates:
            serial = serial_string(quad)
            candidate_flag = decrypt_with_key(ciphertext, serial)
            match = FLAG_RE.search(candidate_flag)
            print(f"[+] serial {serial!r} decrypts to {candidate_flag!r}")
            if match:
                flag = match.group(0)
                break

    if flag is None:
        print("[-] no candidate serial decrypted to a well-formed flag", file=sys.stderr)
        return 1

    print(f"[+] recovered flag: {flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
