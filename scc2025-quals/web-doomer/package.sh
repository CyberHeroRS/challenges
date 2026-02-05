set -e
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "web-doomer.zip" ]; then
  rm -f web-doomer.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
rm -rf node_modules public
zip -r web-doomer.zip .
cd ..
mv ./package/web-doomer.zip ./
rm -rf ./package
