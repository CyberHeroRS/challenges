#!/bin/bash

docker build --no-cache --file Dockerfile.build --output . .

patchelf --set-rpath glibc/ bigvm2
patchelf --set-interpreter glibc/ld-linux-x86-64.so.2 bigvm2