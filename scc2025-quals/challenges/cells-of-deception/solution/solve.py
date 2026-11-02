#!/usr/bin/env python3
"""
Solver for "Cells of Deception".

important.xlsm ships an Auto_Open VBA macro that reads 444 scattered cells
(in a specific row/col order baked into the macro) from the single hidden
worksheet, concatenates their values into a PowerShell script, drops it to
disk and runs it. The script itself is wrapped in two layers of obfuscation
(Base64 -> UTF8 text, then a PowerShell `[char[]](...) -join ''` literal)
before reaching the real payload, which RC4/XOR-decrypts two Base64 blobs
and exfiltrates the result as "secret"/"auth" fields of a JSON beacon.

Concatenating the decrypted "secret" and "auth" values reconstructs the
flag. Nothing here is hardcoded: the cell order comes from parsing the
real VBA macro, the cell values come from the real worksheet, and the
RC4/XOR keys & ciphertexts come from parsing the real deobfuscated script.
"""
import base64
import re
import sys

import openpyxl
from oletools.olevba import VBA_Parser

XLSM_PATH = "important.xlsm"


def extract_vba_source(path):
    parser = VBA_Parser(path)
    sources = []
    for (_, _, _, code) in parser.extract_macros():
        if code:
            sources.append(code)
    parser.close()
    return "\n".join(sources)


def extract_cell_order(vba_source):
    """Pull the exact Sheet.Cells(row, col) order used by Auto_Open."""
    sheet_match = re.search(r'Sheets\("([^"]+)"\)', vba_source)
    sheet_name = sheet_match.group(1) if sheet_match else None
    coords = [
        (int(r), int(c))
        for r, c in re.findall(r"Cells\((\d+),\s*(\d+)\)", vba_source)
    ]
    return sheet_name, coords


def reconstruct_script(xlsm_path, sheet_name, coords):
    wb = openpyxl.load_workbook(xlsm_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.worksheets[0]
    parts = []
    for row, col in coords:
        value = ws.cell(row=row, column=col).value
        parts.append(value if value else "")
    return "".join(parts)


def decode_base64_wrapper(script):
    """$e = [System.Convert]::FromBase64String('...'); ... GetString($e)"""
    m = re.search(r"FromBase64String\('([^']+)'\)", script)
    if not m:
        raise ValueError("base64 wrapper not found in reconstructed script")
    raw = base64.b64decode(m.group(1))
    return raw.decode("utf-8")


def decode_chararray_wrapper(script):
    """$obfuscated = $([char[]]('a','b',...) -join ''); Invoke-Expression ..."""
    m = re.search(r"\[char\[\]\]\((.*?)\)\s*-join\s*''", script, re.S)
    if not m:
        raise ValueError("char[] wrapper not found")
    body = m.group(1)
    tokens = re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", body)
    chars = []
    for single, double in tokens:
        tok = single if single else double
        tok = (
            tok.replace("`$", "$")
            .replace("`n", "\n")
            .replace("`t", "\t")
            .replace("`r", "\r")
            .replace("``", "`")
        )
        chars.append(tok)
    return "".join(chars)


def strip_obfuscation_backticks(script):
    """Outside of the char-array layer, the author backtick-escapes plain
    punctuation (e.g. `( `) `,) purely to dodge static scanners; it always
    collapses to the literal following character."""
    return re.sub(r"`(.)", r"\1", script)


def find_matching_brace(text, open_idx):
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced braces")


def extract_functions(script):
    """Return {name: (params, body)} and the remaining top-level script."""
    functions = {}
    remaining = []
    pos = 0
    for m in re.finditer(r"function\s+([A-Za-z0-9_-]+)\s*(?:\(([^)]*)\))?\s*\{", script):
        remaining.append(script[pos:m.start()])
        open_idx = m.end() - 1
        close_idx = find_matching_brace(script, open_idx)
        body = script[open_idx + 1:close_idx]
        param_str = m.group(2) or ""
        params = [p.strip().lstrip("$") for p in param_str.split(",") if p.strip()]
        functions[m.group(1)] = (params, body)
        pos = close_idx + 1
    remaining.append(script[pos:])
    return functions, "".join(remaining)


def apply_rc4(key, data):
    key_b = [ord(c) for c in key]
    data_b = [ord(c) for c in data]
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key_b[i % len(key_b)]) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = []
    for n in range(len(data_b)):
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(chr(data_b[n] ^ s[(s[i] + s[j]) % 256]))
    return "".join(out)


def apply_xor(data, key):
    return "".join(chr(ord(data[n]) ^ ord(key[n % len(key)])) for n in range(len(data)))


def decode_base64_string(s):
    return base64.b64decode(s).decode("utf-8", errors="replace")


def classify_functions(functions):
    """Map generic function names (random per-build) to the operation they
    implement, purely by inspecting their body - no hardcoded names."""
    roles = {}
    for name, (params, body) in functions.items():
        if "0..255" in body and "-bxor" in body:
            roles["rc4"] = (name, params)
        elif "-bxor" in body:
            roles["xor"] = (name, params)
        elif "FromBase64String" in body and "GetString" in body:
            roles["b64decode"] = (name, params)
        elif '["secret"]' in body and '["auth"]' in body:
            secret_param = re.search(r'\["secret"\]\s*=\s*\$(\w+)', body).group(1)
            auth_param = re.search(r'\["auth"\]\s*=\s*\$(\w+)', body).group(1)
            roles["transmit"] = (name, params, secret_param, auth_param)
    return roles


class Interp:
    """Minimal evaluator for the handful of PowerShell constructs the
    payload actually uses: string literals, variable refs, string
    concatenation with '+', and calls to the classified helper
    functions (possibly nested via parens)."""

    def __init__(self, roles):
        self.vars = {}
        self.roles = roles
        self.transmit_args = None

    def call(self, fname, args):
        if self.roles.get("rc4") and fname == self.roles["rc4"][0]:
            key, data = args
            return apply_rc4(key, data)
        if self.roles.get("xor") and fname == self.roles["xor"][0]:
            data, key = args
            return apply_xor(data, key)
        if self.roles.get("b64decode") and fname == self.roles["b64decode"][0]:
            (s,) = args
            return decode_base64_string(s)
        if self.roles.get("transmit") and fname == self.roles["transmit"][0]:
            self.transmit_args = args
            return None
        raise ValueError(f"unhandled call to {fname}")

    def eval_expr(self, expr):
        expr = expr.strip()
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (
            expr.startswith("'") and expr.endswith("'")
        ):
            return expr[1:-1]
        # Parenthesised call or expression
        if expr.startswith("(") and expr.endswith(")"):
            return self.eval_expr(expr[1:-1])
        # Concatenation
        if "+" in expr and not expr.startswith("$"):
            pass
        parts = self.split_top_level(expr, "+")
        if len(parts) > 1:
            return "".join(self.eval_expr(p) for p in parts)
        # Function call: Name arg arg ...
        call_m = re.match(r"^([A-Za-z0-9_-]+)\s+(.+)$", expr)
        if call_m and not expr.startswith("$"):
            fname = call_m.group(1)
            arg_str = call_m.group(2)
            args = [self.eval_expr(a) for a in self.split_args(arg_str)]
            return self.call(fname, args)
        # Plain variable reference
        if expr.startswith("$"):
            name = expr[1:]
            if name in self.vars:
                return self.vars[name]
            raise ValueError(f"unknown variable {expr}")
        raise ValueError(f"cannot evaluate expression: {expr!r}")

    @staticmethod
    def split_top_level(s, sep):
        parts = []
        depth = 0
        quote = None
        buf = ""
        i = 0
        while i < len(s):
            c = s[i]
            if quote:
                buf += c
                if c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
                buf += c
            elif c == "(":
                depth += 1
                buf += c
            elif c == ")":
                depth -= 1
                buf += c
            elif c == sep and depth == 0:
                parts.append(buf)
                buf = ""
            else:
                buf += c
            i += 1
        parts.append(buf)
        return [p.strip() for p in parts if p.strip()]

    def split_args(self, s):
        # Arguments are whitespace separated at depth 0 (outside parens/quotes)
        args = []
        depth = 0
        quote = None
        buf = ""
        i = 0
        while i < len(s):
            c = s[i]
            if quote:
                buf += c
                if c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
                buf += c
            elif c == "(":
                depth += 1
                buf += c
            elif c == ")":
                depth -= 1
                buf += c
            elif c.isspace() and depth == 0:
                if buf.strip():
                    args.append(buf.strip())
                buf = ""
            else:
                buf += c
            i += 1
        if buf.strip():
            args.append(buf.strip())
        return args

    def run_statement(self, stmt):
        stmt = stmt.strip()
        if not stmt:
            return
        m = re.match(r"^\$([A-Za-z0-9_]+)\s*=\s*(.+)$", stmt, re.S)
        if m:
            name, expr = m.group(1), m.group(2)
            try:
                self.vars[name] = self.eval_expr(expr)
            except (ValueError, IndexError, KeyError, AttributeError):
                pass  # irrelevant statement we don't need (e.g. building "GetBytes")
            return
        # Bare call, e.g. TransmitSystemData $a $b $c
        call_m = re.match(r"^([A-Za-z0-9_-]+)\s+(.+)$", stmt, re.S)
        if call_m:
            try:
                fname = call_m.group(1)
                args = [self.eval_expr(a) for a in self.split_args(call_m.group(2))]
                self.call(fname, args)
            except (ValueError, IndexError, KeyError, AttributeError):
                pass  # statement irrelevant to flag reconstruction (e.g. Get-WmiObject)


def split_statements(script):
    # Statements are separated by newlines; keep only non-empty ones and
    # drop anything referencing live system / network APIs we don't model.
    stmts = []
    for line in script.split("\n"):
        line = line.strip()
        if not line:
            continue
        stmts.append(line)
    return stmts


def main():
    vba_source = extract_vba_source(XLSM_PATH)
    sheet_name, coords = extract_cell_order(vba_source)
    if not coords:
        raise SystemExit("could not find any Cells(row, col) references in the macro")

    layer_a = reconstruct_script(XLSM_PATH, sheet_name, coords)
    layer_b = decode_base64_wrapper(layer_a)
    layer_c = decode_chararray_wrapper(layer_b)
    layer_c = strip_obfuscation_backticks(layer_c)

    functions, top_level = extract_functions(layer_c)
    roles = classify_functions(functions)
    if "transmit" not in roles:
        raise SystemExit("could not identify the exfiltration function")

    interp = Interp(roles)
    for stmt in split_statements(top_level):
        interp.run_statement(stmt)

    if interp.transmit_args is None:
        raise SystemExit("exfiltration call was never reached")

    _, params, secret_param, auth_param = roles["transmit"]
    secret = interp.transmit_args[params.index(secret_param)]
    auth = interp.transmit_args[params.index(auth_param)]

    flag = secret + auth
    print(flag)


if __name__ == "__main__":
    main()
