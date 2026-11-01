#!/bin/bash

docker build -t loooose .
docker run -d -p 9050:80 loooose