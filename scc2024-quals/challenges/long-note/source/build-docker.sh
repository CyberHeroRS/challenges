#!/bin/bash

docker build -t longnote .
docker run -d -p 7777:7777 longnote
