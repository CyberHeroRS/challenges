#!/usr/bin/env python3
"""
Solver for "SpookyMacro".

secret.docm ships a VBA macro (NewMacros.bas, Sub secret_macro) that never
writes the flag out directly: it builds an array of integer "ASCII values",
runs each one through a small per-character arithmetic expression (here
`+ 1 - 1`, a no-op added purely to obscure the intent) and converts every
resulting code point with Chr() into a character, concatenating all of them
into the `flag` variable. The macro then only shows a decoy MsgBox with a
YouTube link - the flag itself is never printed or used anywhere else in
the document, it's hidden purely in how the obfuscated array decodes.

Nothing here is hardcoded: the integer array and the per-element arithmetic
expression are both parsed straight out of the real macro source and
evaluated generically, so this recovers the flag for whatever numbers/
expression the macro actually contains.
"""
import ast
import operator
import re

from oletools.olevba import VBA_Parser

DOCM_PATH = "secret.docm"

# Only simple arithmetic is expected in the per-character expression
# (e.g. "asciiValues(i) + 1 - 1"); restrict evaluation to these operators.
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
}


def extract_vba_source(path):
    parser = VBA_Parser(path)
    sources = []
    for (_, _, _, code) in parser.extract_macros():
        if code:
            sources.append(code)
    parser.close()
    return "\n".join(sources)


def extract_ascii_array(vba_source):
    """Pull the integer list out of `<name> = Array(1, 2, 3, _\\n 4, ...)`."""
    match = re.search(r"(\w+)\s*=\s*Array\((.*?)\)\s*\n", vba_source, re.S)
    if not match:
        raise SystemExit("could not find an Array(...) literal in the macro")
    array_name = match.group(1)
    body = match.group(2)
    # Drop VBA line-continuation underscores before splitting on commas.
    body = body.replace("_", " ")
    values = [int(tok.strip()) for tok in body.split(",") if tok.strip()]
    return array_name, values


def extract_char_code_expr(vba_source, array_name):
    """Find the `charCode = <expr involving array_name(i)>` assignment."""
    pattern = rf"charCode\s*=\s*(.+)"
    match = re.search(pattern, vba_source)
    if not match:
        raise SystemExit("could not find a charCode assignment in the macro")
    expr = match.group(1).strip()
    # Replace the VBA array-index call with a plain identifier so it parses
    # as Python, e.g. "asciiValues(i) + 1 - 1" -> "value + 1 - 1".
    expr = re.sub(rf"{array_name}\s*\(\s*i\s*\)", "value", expr)
    return expr


def eval_expr(expr, value):
    """Safely evaluate a restricted arithmetic expression for one `value`."""
    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id == "value":
            return value
        raise ValueError(f"unsupported expression node: {ast.dump(node)}")

    return int(_eval(tree))


def main():
    vba_source = extract_vba_source(DOCM_PATH)
    array_name, values = extract_ascii_array(vba_source)
    expr = extract_char_code_expr(vba_source, array_name)
    flag = "".join(chr(eval_expr(expr, value)) for value in values)
    print(flag)


if __name__ == "__main__":
    main()
