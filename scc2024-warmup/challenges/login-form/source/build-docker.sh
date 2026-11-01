#!/bin/bash
docker build --network host --tag=pwn_login_form .
docker run -d -it -p 1340:1337 --privileged --rm --name=pwn_login_form pwn_login_form
