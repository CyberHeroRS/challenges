#!/bin/bash

DOCKER_IMAGE="debian:bullseye-slim"
SOURCE_FILE="source.c"
OUTPUT_FILE="fancy"

docker run --rm -v $(pwd):/src $DOCKER_IMAGE bash -c "
    apt-get update && \
    apt-get install -y gcc make && \
    gcc /src/$SOURCE_FILE -o /src/$OUTPUT_FILE
"