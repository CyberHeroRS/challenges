#!/bin/bash

docker build --no-cache --file Dockerfile.build --output . .

patchelf --set-rpath . beus3
patchelf --set-interpreter ./ld-linux-x86-64.so.2 beus3