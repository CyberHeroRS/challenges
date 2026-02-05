#!/bin/bash
set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-toddler-jumble.zip" ]; then
    rm pwn-toddler-jumble.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-toddler-jumble.zip .
cd ..
mv ./package/pwn-toddler-jumble.zip ./pwn-toddler-jumble.zip 
rm -rf ./package
