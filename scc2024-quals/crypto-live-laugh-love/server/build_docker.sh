#!/bin/bash
docker build -t live-laugh-love .
docker run --rm -d -p 13300:13300 --name live-laugh-love live-laugh-love
