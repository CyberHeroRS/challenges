#!/bin/bash
docker build --network host --tag=pwn_outer .
docker run -d -it -p 1339:5000 --privileged --rm --name=pwn_outer pwn_outer
