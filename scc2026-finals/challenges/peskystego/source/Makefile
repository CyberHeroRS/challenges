.PHONY: all compile testrun testandclean clean

CC = gcc
CFLAGS = -lpng -O2 -Wall -Wextra -Werror
CHALL_NAME := $(notdir $(CURDIR))

all: compile

compile: stego.c decode.c
	mkdir -p build
	gcc stego.c $(CFLAGS) -s -o build/stego
	gcc decode.c $(CFLAGS) -o build/decode

testrun: compile image.png
	./build/stego image.png out.png "hello world"
	./build/decode out.png

testandclean: testrun clean

dist: compile
	tar -czvf $(CHALL_NAME).tar.gz \
		--transform="s|^build/|$(CHALL_NAME)/|" \
		--transform="s|^output.png|$(CHALL_NAME)/output.png|" \
		build/stego output.png

clean:
	rm -rf build
