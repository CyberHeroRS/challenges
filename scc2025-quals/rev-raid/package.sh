#!/bin/bash
set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-raid.zip" ]; then
    rm pwn-raid.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r pwn-raid.zip .
cd ..
mv ./package/pwn-raid.zip ./rev-raid.zip 
rm -rf ./package
