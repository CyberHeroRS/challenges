#!/bin/bash
docker build --network host --tag=ghost_activity .
docker run -d -it -p 1500:1500 --privileged --rm --name=ghost_activity ghost_activity 
