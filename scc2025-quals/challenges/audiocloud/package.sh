set -e
mkdir -p ./public
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "./public/web-audiocloud.zip" ]; then
    rm -f ./public/web-audiocloud.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web-audiocloud.zip .
cd ..
mv ./package/web-audiocloud.zip ./public/web-audiocloud.zip
rm -rf ./package
