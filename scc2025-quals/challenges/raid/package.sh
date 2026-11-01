#!/bin/bash
set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/rev-raid.zip" ]; then
    rm -f ./public/rev-raid.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-raid.zip .
cd ..
mv ./package/pwn-raid.zip ./public/rev-raid.zip
rm -rf ./package
