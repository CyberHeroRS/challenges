#!/bin/bash
set -euo pipefail
docker build --tag=pwn_bananas_shop .
docker run -d -it -p 1338:1337 --cap-drop=ALL --security-opt=no-new-privileges --rm --name=pwn_bananas_shop pwn_bananas_shop
