#!/bin/bash
docker build -t hades-ii .
docker run --rm -d -p 13301:13301 --name hades-ii hades-ii