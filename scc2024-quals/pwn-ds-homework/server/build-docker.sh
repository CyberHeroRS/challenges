#!/bin/bash
docker build --network host --tag=linked_list .
docker run -d -it -p 1338:5000 --privileged --rm --name=linked_list linked_list 
