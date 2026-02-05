#!/bin/bash
docker build --network host --tag=what_does_the_fox_say .
docker run -d -it -p 1501:1501 --privileged --rm --name=what_does_the_fox_say what_does_the_fox_say
