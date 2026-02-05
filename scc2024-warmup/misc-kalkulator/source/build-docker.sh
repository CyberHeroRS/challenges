#!/bin/bash
docker build --network host --tag=misc_kalkulator .
docker run -d -it -p 1337:5000 --privileged --rm --name=misc_kalkulator misc_kalkulator
