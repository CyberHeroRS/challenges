default := build
CHALL := $(notdir $(CURDIR))
DIST_DIR := dist
CC6502 ?= cl65
CFLAGS ?= -tc64 -Os
EMULATOR ?= x64sc

.PHONY: build dist run clean

build: main.c gen_flag.py flag.txt
	python3 gen_flag.py
	mkdir -p $(DIST_DIR)
	$(CC6502) $(CFLAGS) main_compile.c -o $(DIST_DIR)/$(CHALL).prg

dist: build
	tar czvf "${CHALL}.tar.gz" --transform "s|^${DIST_DIR}|$(CHALL)|g" dist/*

run: build
	$(EMULATOR) $(DIST_DIR)/$(CHALL).prg

clean:
	-rm -rf main_compile.c $(DIST_DIR) "${CHALL}.tar.gz"
	-rm *.o
