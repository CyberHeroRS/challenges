#!/bin/bash


# pow
random_string=$(mktemp -u XXXXXXXXXX)
hashcash_command="hashcash -mb28 $random_string"

echo "$hashcash_command"
echo -n "hashcash stamp: "
read -r proof_of_work

if hashcash -c -r "$random_string" -b 28 -d "$proof_of_work"; then
    echo "Successful: Proof of work is valid."
else
    echo "Failed: Proof of work is invalid."
    exit 1
fi


# get exploit
echo "Please provide a URL to download exploit:"
read -r URL

TEMPFILE=$(mktemp)

if [[ $URL =~ ^https?:// ]]; then
    curl -k -s -o "$TEMPFILE" --max-filesize 10M -A 'SCC' -- "$URL"
fi

chmod 777 "$TEMPFILE"


# actuall challenge
exec timeout --foreground 300 \
qemu-system-x86_64 \
	-append "console=ttyS0 debug earlyprintk=serial oops=panic selinux=0 pti tsc=unstable panic=1000 cgroup_disable=memory" \
	-boot order=d \
	-cpu kvm64 \
	-drive file="$TEMPFILE",format=raw \
	-initrd initramfs.cpio.gz \
	-kernel ./bzImage \
	-m 128M \
	-monitor none,server,nowait,nodelay,reconnect=-1 \
	-nographic \
	-no-reboot \
	-smp cores=1,threads=2 \
	-snapshot \
	2>&1
