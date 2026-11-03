import importlib.util
import marshal
import os

# mamba.pyc is a genuine CPython 3.12.4 code object (built fresh at image build
# time, see ../source/Dockerfile): un-marshal it directly and read its
# co_consts to recover the embedded scrambled string + permutation table,
# exactly as the published source does -- no decompiler needed, no flag
# hardcoded.

PYC_PATH = "/solution/mamba.pyc"

with open(PYC_PATH, "rb") as f:
    # Standard (non hash-based) pyc header: 4-byte magic + 4-byte bit field +
    # 4-byte mtime + 4-byte source size = 16 bytes, per PEP 552.
    header = f.read(16)
    assert header[:4] == importlib.util.MAGIC_NUMBER, (
        f"magic number mismatch: pyc was built for a different Python version "
        f"than this solver ({header[:4]!r} != {importlib.util.MAGIC_NUMBER!r})"
    )
    code = marshal.load(f)

consts = code.co_consts
# consts contains: the scrambled string, the permutation tuple, and some
# literal strings/None used by the script -- find them by type/shape rather
# than by position, so this keeps working even if literal ordering shifts.
scrambled = next(c for c in consts if isinstance(c, str) and len(c) > 20)
indices = next(
    c
    for c in consts
    if isinstance(c, tuple) and len(c) == len(scrambled) and all(isinstance(x, int) for x in c)
)

flag = "".join(scrambled[indices.index(i)] for i in range(len(scrambled)))
print(flag)

expected = os.environ.get("flag_main")
if expected and expected not in flag:
    print(f"MISMATCH: expected substring {expected!r} not in decoded flag {flag!r}")
    raise SystemExit(1)
