#!/bin/bash
docker build -t hades .
docker run --rm -d -p 13300:13300 --name hades hades