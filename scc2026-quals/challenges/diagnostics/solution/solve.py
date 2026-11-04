import base64
import os
import re

import requests

HOST = os.environ.get("SERVICE_DIAGNOSTICS_WEB_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_DIAGNOSTICS_WEB_PORT", "4545")
BASE_URL = f"http://{HOST}:{PORT}"

# A "scavenger hunt" across every surface a browser can expose: 8 flag
# shards hidden in an HTML comment, a CSS comment, a console.log call,
# a response header, robots.txt, base64-in-localStorage (seeded by
# inline JS), a minified-JS trailing comment, and a source map's
# embedded source content.

parts = {}


def grab(label, text_source, pattern):
    m = re.search(pattern, text_source)
    if not m:
        raise SystemExit(f"could not find {label}")
    parts[label] = m.group(1)


index_html = requests.get(f"{BASE_URL}/index.html", timeout=15).text
# The HTML comment literally reads "pt1{SCC{d14gn05t1c_}" -- the "SCC{"
# there is a hint about the overall flag format, not part of the shard
# itself (the real content is whatever sits between it and the single
# closing brace).
grab("1", index_html, r"FLAG_PART_A=pt1\{SCC\{([^}]*)\}")

style_css = requests.get(f"{BASE_URL}/assets/style.css", timeout=15).text
grab("2", style_css, r"FLAG_PART_B=pt2\{([^}]*)\}")

app_js = requests.get(f"{BASE_URL}/assets/app.js", timeout=15).text
# FLAG_PART_C is only printed via a browser console.log() template
# literal (`FLAG_PART_C=pt3{${BOOT_TAG}}`) -- since we're just fetching
# the raw JS source rather than executing it, pull BOOT_TAG's literal
# value directly instead.
boot_tag = re.search(r'BOOT_TAG\s*=\s*"([^"]*)"', app_js).group(1)
parts["3"] = boot_tag

pulse = requests.get(f"{BASE_URL}/api/pulse", timeout=15)
relay = pulse.headers.get("x-diagnostic-relay", "")
grab("4", relay, r"FLAG_PART_D=pt4\{([^}]*)\}")

robots = requests.get(f"{BASE_URL}/robots.txt", timeout=15).text
grab("5", robots, r"FLAG_PART_E=pt5\{([^}]*)\}")

# FLAG_PART_F is base64-seeded into localStorage by app.js; replicate
# the decode directly from the same literal constant.
m = re.search(r'STORAGE_VAL\s*=\s*"([^"]+)"', app_js)
decoded_f = base64.b64decode(m.group(1)).decode()
grab("6", decoded_f, r"pt6\{([^}]*)\}")

runtime_js = requests.get(f"{BASE_URL}/assets/runtime.min.js", timeout=15).text
grab("7", runtime_js, r"FLAG_PART_G=pt7\{([^}]*)\}")

source_map = requests.get(f"{BASE_URL}/assets/source_part.js.map", timeout=15).text
grab("8", source_map, r"pt8\{([^}]*)\}")

flag_body = "".join(parts[str(i)] for i in range(1, 9))
flag = f"SCC{{{flag_body}}}"
print(flag)

flag_env = os.environ.get("flag_flag")
if flag_env and flag_env not in flag:
    raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")
