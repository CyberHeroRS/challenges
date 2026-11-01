#!/bin/bash
docker build --network host --tag=zork1 .
docker run -d -it -p 4999:1337 --privileged --rm --name=zork1 zork1
