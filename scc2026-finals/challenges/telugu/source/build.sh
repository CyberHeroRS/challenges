#!/bin/bash

docker build -t builder -f Dockerfile.build .
docker run --rm -v $(pwd):/build -u $(id -u):$(id -g) builder bash -c "\
	gcc -o main chall/shell.c \
	  -Wl,--rpath=. \
		-Wl,--dynamic-linker=./ld-linux-x86-64.so.2
"

cid=$(docker create --name temp builder)
docker cp $cid:/lib/x86_64-linux-gnu/ld-2.31.so ./ld-linux-x86-64.so.2
docker cp $cid:/lib/x86_64-linux-gnu/libc-2.31.so ./libc.so.6
docker rm -f $cid

env LD_TRACE_LOADED_OBJECTS=1 ./main
