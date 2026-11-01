set -e
mkdir -p ./public
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "./public/web-doomer.zip" ]; then
    rm -f ./public/web-doomer.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
rm -rf node_modules public
zip -r web-doomer.zip .
cd ..
mv ./package/web-doomer.zip ./public/web-doomer.zip
rm -rf ./package
