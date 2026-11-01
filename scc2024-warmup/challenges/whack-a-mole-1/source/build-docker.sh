#!/bin/bash
docker build --network host --tag=crypto_whack_a_mole .
docker run -d -it -p 4991:1337 --privileged --rm --name=crypto_whack_a_mole crypto_whack_a_mole
