#!/bin/bash
docker rm -f web_anatomy
docker build --tag=web_anatomy .
docker run -d -p 1337:1337 -it --rm --name=web_anatomy web_anatomy
