.PHONY: all clean

all: callgate.bpf.o callgate.skel.h callgate

callgate.bpf.o: callgate.bpf.c
	clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -I/usr/include/x86_64-linux-gnu -c $< -o $@

callgate.skel.h: callgate.bpf.o
	bpftool gen skeleton $< > $@

callgate: callgate.c callgate.skel.h
	gcc -O2 -Wall -I. -o $@ $< -lbpf -lelf -lz

clean:
	rm -f callgate callgate.bpf.o callgate.skel.h