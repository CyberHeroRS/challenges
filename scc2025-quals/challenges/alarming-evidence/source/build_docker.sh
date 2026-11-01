#!/bin/bash
docker build --network host --tag=alarming_evidence .
docker run -d -it -p 1501:1501 --privileged --rm --name=alarming_evidence alarming_evidence