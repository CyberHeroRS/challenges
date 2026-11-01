
all: strcatenator

# -Se -> stop on error
# -Cg -> position independent code
# -Ct -> canary
# -bl -> all debug symbols ???
# -g -> gdb debug symbols
%: %.pas
	fpc -Cg -Se -bl -g $^

clean:
	rm -f strcatenator.o strcatenator
