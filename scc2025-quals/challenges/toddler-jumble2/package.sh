#!/bin/bash
set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-toddler-jumble2.zip" ]; then
    rm -f ./public/pwn-toddler-jumble2.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-toddler-jumble2.zip .
cd ..
mv ./package/pwn-toddler-jumble2.zip ./public/pwn-toddler-jumble2.zip
rm -rf ./package
