#!/bin/bash
docker build --network host --tag=serbian_rop .
docker run -d -it -p 1337:5000 --privileged --rm --name=serbian_rop serbian_rop
