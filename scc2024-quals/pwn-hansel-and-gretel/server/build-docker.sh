#!/bin/bash
docker build --network host --tag=hansel_and_gretel .
docker run -d -it -p 1400:9001 --privileged --rm --name=hansel_and_gretel hansel_and_gretel
