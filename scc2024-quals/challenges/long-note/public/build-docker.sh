#!/bin/bash

docker build -t longnote .
docker run -p 7777:7777 longnote
