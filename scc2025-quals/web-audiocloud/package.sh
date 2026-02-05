set -e
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "web-audiocloud.zip" ]; then
  rm -f web-audiocloud.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web-audiocloud.zip .
cd ..
mv ./package/web-audiocloud.zip ./
rm -rf ./package
