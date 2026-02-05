#!/bin/bash

docker build -t glibc-2.27-build -f Dockerfile.build .
docker run --rm -v $(pwd):/build -u $(id -u):$(id -g) glibc-2.27-build bash -c "\
	gcc -o app app.c \
	  -Wl,--rpath=. \
		-Wl,--dynamic-linker=./ld-linux-x86-64.so.2
"

cid=$(docker create --name temp ubuntu:18.04)
docker cp $cid:/lib/x86_64-linux-gnu/ld-2.27.so ./ld-linux-x86-64.so.2
docker cp $cid:/lib/x86_64-linux-gnu/libc-2.27.so ./libc.so.6
docker rm -f $cid

env LD_TRACE_LOADED_OBJECTS=1 ./app
