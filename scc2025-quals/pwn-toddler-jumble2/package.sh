#!/bin/bash
set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-toddler-jumble2.zip" ]; then
    rm pwn-toddler-jumble2.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-toddler-jumble2.zip .
cd ..
mv ./package/pwn-toddler-jumble2.zip ./pwn-toddler-jumble2.zip 
rm -rf ./package
