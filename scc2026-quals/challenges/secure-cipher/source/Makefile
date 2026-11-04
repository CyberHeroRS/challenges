all: secure-cipher

secure-cipher: source.c
	zig cc source.c -o secure-cipher -fno-sanitize=all -fno-stack-protector -static -no-pie -target aarch64-linux-musl
