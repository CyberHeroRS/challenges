#!/bin/bash
set -euo pipefail

if ! mountpoint -q /sys/fs/bpf; then
    mount -t bpf bpf /sys/fs/bpf
fi
if ! mountpoint -q /sys/kernel/tracing; then
    mount -t tracefs nodev /sys/kernel/tracing
fi
if ! mountpoint -q /sys/kernel/debug; then
    mount -t debugfs nodev /sys/kernel/debug
fi

/home/ctf/callgate &
DAEMON_PID=$!

sleep 1

if ! kill -0 "$DAEMON_PID" 2>/dev/null; then
    echo "[!] callgate daemon failed to start" >&2
    exit 1
fi

unset FLAG
exec socat TCP-LISTEN:1337,reuseaddr,fork EXEC:"bash --login",su=ctf,stderr