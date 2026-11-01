#!/bin/bash
docker build --network host --tag=pwn_bananas_shop .
docker run -d -it -p 1338:1337 --privileged --rm --name=pwn_bananas_shop pwn_bananas_shop
