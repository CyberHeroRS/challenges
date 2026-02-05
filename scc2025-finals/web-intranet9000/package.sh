#!/bin/sh
set -e

category=web
chall=intranet9000

if [ -d "./package" ]; then
    rm -rf ./package
fi

if [ -f "$category-$chall.zip" ]; then
    rm -f $category-$chall.zip
fi

mkdir ./package

cp -r ./source/* ./package/

cd ./package
zip -r $category-$chall.zip .

cd ..
mv ./package/$category-$chall.zip ./$category-$chall.zip
rm -rf ./package
