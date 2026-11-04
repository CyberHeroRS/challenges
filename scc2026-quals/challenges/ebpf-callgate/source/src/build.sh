#!/bin/bash
set -euo pipefail

SOURCE_DIR="$(dirname "$0")"
OUT_DIR="$SOURCE_DIR/../binary"

mkdir -p "$OUT_DIR"

docker build \
	--target export \
	--output type=local,dest="$OUT_DIR" \
	-f "$SOURCE_DIR/Dockerfile.build" \
	"$SOURCE_DIR"