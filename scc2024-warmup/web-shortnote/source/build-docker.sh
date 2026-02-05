#!/bin/bash

docker build -t shortnote .
docker run -d -p 7777:7777 shortnote
