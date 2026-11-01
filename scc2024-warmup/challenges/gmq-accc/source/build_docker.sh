#!/bin/bash

docker build --network host --tag=misc_gmq_accc .
docker run -d -it -p 1337:1337 --privileged --rm --name=misc_gmq_accc misc_gmq_accc
