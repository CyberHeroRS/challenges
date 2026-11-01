#!/bin/bash
set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-toddler-jumble.zip" ]; then
    rm -f ./public/pwn-toddler-jumble.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-toddler-jumble.zip .
cd ..
mv ./package/pwn-toddler-jumble.zip ./public/pwn-toddler-jumble.zip
rm -rf ./package
