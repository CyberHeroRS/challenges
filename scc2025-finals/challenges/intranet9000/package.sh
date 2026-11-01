#!/bin/sh
set -e
mkdir -p ./public

category=web
chall=intranet9000

if [ -d "./package" ]; then
    rm -rf ./package
fi

if [ -f "./public/web-intranet9000.zip" ]; then
    rm -f ./public/web-intranet9000.zip
fi

mkdir ./package

cp -r ./source/* ./package/

cd ./package
zip -r $category-$chall.zip .

cd ..
mv ./package/$category-$chall.zip ./public/web-intranet9000.zip
rm -rf ./package
