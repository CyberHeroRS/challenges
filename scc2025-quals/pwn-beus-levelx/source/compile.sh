#!/bin/bash

DOCKER_IMAGE="debian:bullseye-slim"
SOURCE_FILE="source.c"
OUTPUT_FILE="beusX"

docker run --rm -v $(pwd):/src $DOCKER_IMAGE bash -c "
    apt-get update && \
    apt-get install -y gcc make && \
    gcc /src/$SOURCE_FILE -o /src/$OUTPUT_FILE -fstack-protector -Wl,-z,relro,-z,now
    cp /lib/x86_64-linux-gnu/libc-2.31.so /src/glibc
    cp /lib/x86_64-linux-gnu/ld-2.31.so /src/glibc
"