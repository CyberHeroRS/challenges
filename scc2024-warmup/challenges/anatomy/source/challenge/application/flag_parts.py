"""Splits the real flag (injected via challenge.yaml's env-based flag
mechanism) into 5 roughly equal chunks, scattered across this challenge's
different "anatomy" layers (raw HTML, CSS, JavaScript, a JSON response body,
and a response header). Splitting is computed from the actual runtime flag
length rather than hardcoded byte offsets, so it stays correct regardless of
the configured flag body/prefix/format.
"""

import math
import os

FLAG = os.environ.get("FLAG", "SCC{placeholder_flag_not_set}")


def split_flag_into_parts(flag: str, n: int = 5):
    chunk_size = math.ceil(len(flag) / n)
    parts = [flag[i:i + chunk_size] for i in range(0, len(flag), chunk_size)]
    while len(parts) < n:
        parts.append("")
    return parts[:n]


FLAG_PARTS = split_flag_into_parts(FLAG)
