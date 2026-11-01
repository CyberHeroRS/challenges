#!/bin/bash
docker rm -f blind_luck
docker build --tag=blind_luck .
docker run -d -p 8080:8080 -p 8081:8081 -it --rm --name=blind_luck blind_luck
