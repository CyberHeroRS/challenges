#!/bin/bash
set -euo pipefail
docker build --tag=zork1 .
docker run -d -it -p 4999:1337 --cap-drop=ALL --security-opt=no-new-privileges --rm --name=zork1 zork1
