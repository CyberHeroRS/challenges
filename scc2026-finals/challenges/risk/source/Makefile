CC=/opt/riscv/bin/riscv32-unknown-linux-gnu-gcc
CFLAGS=--static -Wall -Wextra

all:
	$(CC) $(CFLAGS) -o main chall/main.c

run:
	qemu-riscv32-static ./main

debug:
	qemu-riscv32-static -g 1234 ./main

gdb:
	gdb -ex "target remote localhost:1234" -ex "set architecture riscv:rv32" -ex "file main"
