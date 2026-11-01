#!/bin/bash
docker rm -f web_flags4everyone
docker build --tag=web_flags4everyone .
docker run -d -p 1337:1337 -it --rm --name=web_flags4everyone web_flags4everyone
