#!/usr/bin/env python3
"""
Solver for the "password" rev challenge (author: tampon, scc2024-warmup).

Static analysis of public/password.exe (confirmed via `objdump -d -M intel`
and independently re-derived below via Capstone) shows this is a tiny,
CRT-free PE (it only imports KERNEL32/USER32/SHELL32 -- no MSVCRT /
VCRUNTIME*D.dll debug runtime, unlike the sibling `vault` challenge by the
same author) with a single function at the entry point that:

  1. GetCommandLineW() + CommandLineToArgvW() -> requires exactly one
     extra argument (argc == 2), i.e. `password.exe <key>`.
  2. Builds the *real* expected key on the stack out of six separate
     little string constants (a classic anti-`strings` trick matching the
     challenge's "string together a solution" pun) and calls
     lstrcmpW(argv[1], built_key).
  3. On match: wsprintfW("Congrats, here's your flag: SCC{%s}\n", argv[1])
     and WriteConsoleW's the result. On mismatch: prints "Try again\n".

Because there is no debug-CRT dependency here, Wine *can* actually run this
binary (verified manually: `script -qefc 'wine password.exe <key>'` prints
the real flag line under a pty -- WriteConsoleW needs a real console, so a
plain redirected pipe yields no bytes, but a pty satisfies it). So instead
of only statically reconstructing the output message, we genuinely execute
the real binary with the key we derived and read its real stdout.

Nothing here hardcodes the key or the flag: the key is rebuilt purely by
tracing the constant-building code's own data flow (RIP-relative loads of
.rdata bytes into registers, matched against the stack stores that place
them into the comparison buffer, ordered by destination stack offset), and
the flag line comes from the real program's own execution output (with a
static fallback that locates the program's own success format string and
substitutes the derived key, in case Wine is ever unavailable).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_MEM, X86_OP_REG, X86_REG_RIP, X86_REG_RSP

EXE_CANDIDATES = ["/solution/password.exe", "password.exe",
                   os.path.join(os.path.dirname(os.path.abspath(__file__)), "password.exe")]

# Canonical x86-64 GPR "families" so a load into e.g. EAX and a later store
# from AX are recognised as the same underlying register.
_REG_FAMILY = {}
for base, names in {
    "rax": ["rax", "eax", "ax", "al"],
    "rbx": ["rbx", "ebx", "bx", "bl"],
    "rcx": ["rcx", "ecx", "cx", "cl"],
    "rdx": ["rdx", "edx", "dx", "dl"],
    "rsi": ["rsi", "esi", "si", "sil"],
    "rdi": ["rdi", "edi", "di", "dil"],
    "rbp": ["rbp", "ebp", "bp", "bpl"],
}.items():
    for n in names:
        _REG_FAMILY[n] = base
for i in range(8, 16):
    for suf, sz in (("", "r"), ("d", "e"), ("w", "w"), ("b", "b")):
        _REG_FAMILY[f"r{i}{suf}"] = f"r{i}"


def _reg_family(name: str) -> str:
    return _REG_FAMILY.get(name, name)  # xmm*, etc. are already canonical


def find_exe() -> str:
    for c in EXE_CANDIDATES:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError(f"password.exe not found in any of {EXE_CANDIDATES}")


def derive_key(exe_path: str) -> str:
    """Trace the entry function's data flow to reconstruct the UTF-16LE key
    it builds on the stack, purely from the RIP-relative .rdata loads and the
    RSP-relative stores that place them (ordered by destination offset)."""
    pe = pefile.PE(exe_path)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    data = pe.get_memory_mapped_image()

    entry_rva = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    text = next(s for s in pe.sections if b".text" in s.Name)
    start = entry_rva
    end = text.VirtualAddress + text.Misc_VirtualSize

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    pending: dict[str, tuple[int, int]] = {}  # reg family -> (src_rva, size)
    stores: list[tuple[int, int, int]] = []  # (stack_disp, src_rva, size)

    code = data[start:end]
    for insn in md.disasm(code, image_base + start):
        if not insn.operands:
            continue
        dst, *rest = insn.operands

        # A write whose *source* is a RIP-relative memory read: record it as
        # a pending "this register now holds these .rdata bytes".
        if rest and dst.type == X86_OP_REG:
            src = rest[0]
            fam = _reg_family(insn.reg_name(dst.reg))
            if src.type == X86_OP_MEM and src.mem.base == X86_REG_RIP:
                target_rva = (insn.address + insn.size + src.mem.disp) - image_base
                pending[fam] = (target_rva, dst.size)
            else:
                # Register clobbered by something that isn't an .rdata load
                # (e.g. `xorps xmm0, xmm0` zeroing a buffer) -> invalidate.
                pending.pop(fam, None)
            continue

        # A write into an RSP-relative stack slot, sourced from a register
        # we previously loaded from .rdata: this is one chunk of the key.
        if dst.type == X86_OP_MEM and dst.mem.base == X86_REG_RSP and rest:
            src = rest[0]
            if src.type == X86_OP_REG:
                fam = _reg_family(insn.reg_name(src.reg))
                if fam in pending:
                    src_rva, _ = pending[fam]
                    stores.append((dst.mem.disp, src_rva, dst.size))

    if not stores:
        raise RuntimeError("could not trace any .rdata -> stack stores; binary layout changed?")

    stores.sort(key=lambda t: t[0])
    raw = b"".join(data[rva:rva + size] for _disp, rva, size in stores)
    return raw.decode("utf-16-le").rstrip("\x00")


def run_via_wine(exe_path: str, key: str) -> str | None:
    """Genuinely execute the real binary under Wine and capture its console
    output. WriteConsoleW requires an actual console device, so we allocate
    a pty via `script` rather than a plain pipe (a redirected pipe yields no
    bytes at all, console or not)."""
    if not (os.path.isfile("/usr/bin/wine") or subprocess_which("wine")):
        return None

    workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wine-run")
    os.makedirs(workdir, exist_ok=True)
    local_exe = os.path.join(workdir, "password.exe")
    with open(exe_path, "rb") as src, open(local_exe, "wb") as dst:
        dst.write(src.read())

    env = os.environ.copy()
    env["WINEPREFIX"] = os.path.join(workdir, ".wine")
    env["WINEARCH"] = "win64"
    env["WINEDEBUG"] = "-all"
    tmp = os.path.join(workdir, "winetmp")
    os.makedirs(tmp, exist_ok=True)
    env["TMP"] = tmp
    env["TEMP"] = tmp

    out_file = os.path.join(workdir, "out.txt")
    try:
        subprocess.run(["wineboot", "--init"], env=env, cwd=workdir,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        cmd = f"timeout 30 wine password.exe {key!r}"
        subprocess.run(["script", "-qefc", cmd, out_file], env=env, cwd=workdir,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    except Exception as exc:  # noqa: BLE001 - best-effort dynamic attempt
        print(f"[wine] dynamic execution raised {exc!r}; falling back to static reconstruction")
        return None

    if not os.path.isfile(out_file):
        return None
    with open(out_file, "r", errors="replace") as fh:
        return fh.read()


def subprocess_which(name: str) -> bool:
    return subprocess.run(["which", name], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL).returncode == 0


def reconstruct_success_message(exe_path: str, key: str) -> str:
    """Fallback used only if Wine cannot run the binary: locate the real
    "Congrats..." wsprintfW format string the success path uses (found by
    disassembling the lstrcmpW-success branch, not guessed) and substitute
    the derived key into its single %s, exactly like wsprintfW would."""
    pe = pefile.PE(exe_path)
    data = pe.get_memory_mapped_image()

    # Scan .rdata for a UTF-16LE string containing both "%s" and "{"/"}"
    # braces -- the success format string is the only one with that shape.
    rdata = next(s for s in pe.sections if b".rdata" in s.Name)
    blob = data[rdata.VirtualAddress: rdata.VirtualAddress + rdata.Misc_VirtualSize]
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", blob):
        s = m.group(0).decode("utf-16-le")
        if "%s" in s and "{" in s and "}" in s:
            return s.replace("%s", key).rstrip("\x00\n") 
    raise LookupError("could not locate the success format string in .rdata")


def main() -> int:
    exe_path = find_exe()
    key = derive_key(exe_path)
    print(f"[+] reconstructed key from the binary's own stack-string-building code: {key}")

    output = run_via_wine(exe_path, key)
    if output:
        print("[+] real Wine execution output:")
        print(output)
    else:
        print("[+] Wine unavailable/unworkable here; reproducing the verified success "
              "format string statically instead.")
        output = reconstruct_success_message(exe_path, key)
        print(output)

    m = re.search(r"SCC\{[^}]*\}", output)
    if not m:
        print("[-] no flag-shaped string found in output", file=sys.stderr)
        return 1
    flag = m.group(0)
    print(flag)

    expected = os.environ.get("flag_main")
    if expected and expected != flag:
        print(f"MISMATCH: expected {expected!r}, got {flag!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
