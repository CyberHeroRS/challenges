#!/bin/bash
set -x
export FLAG='SCC{too_much_blinding}'
while true; do
    python3 sc9000.py > output.txt
    timeout --kill-after=5 30 sage -python ../checker/solution.py
    if [ $? -eq 0 ]
    then
        break
    fi
done