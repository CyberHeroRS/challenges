#!/bin/sh
#gcc -o exploit -static $1
#mv ./exploit ./initramfs
cd initramfs || exit
find . -print0 \
| cpio --null -ov --format=newc \
| gzip -9 > ../initramfs.cpio.gz
cd ..
