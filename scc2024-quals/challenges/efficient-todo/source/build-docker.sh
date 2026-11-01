#!/bin/bash
docker build --network host --tag=efficient_todo .
docker run -d -it -p 6969:6969 --privileged --rm --name=efficient_todo efficient_todo
