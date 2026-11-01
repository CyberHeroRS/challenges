#!/bin/bash
set -euo pipefail
docker build --tag=pwn_login_form .
docker run -d -it -p 1340:1337 --cap-drop=ALL --security-opt=no-new-privileges --rm --name=pwn_login_form pwn_login_form
