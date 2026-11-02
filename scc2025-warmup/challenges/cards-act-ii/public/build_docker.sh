#!/bin/bash
docker build -t cards-act-ii .
docker run --rm -d -p 13300:13300 --name cards-act-ii cards-act-ii
