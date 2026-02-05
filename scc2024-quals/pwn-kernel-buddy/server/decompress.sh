#!/bin/sh

mkdir -p initramfs
cd initramfs || exit
cp ../initramfs.cpio.gz .
gunzip ./initramfs.cpio.gz
cpio -idm < ./initramfs.cpio
rm initramfs.cpio
cd ..
