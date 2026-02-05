set -e
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "web-waffles.zip" ]; then
  rm -f web-waffles.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
rm -rf waf/target
zip -r web-waffles.zip .
cd ..
mv ./package/web-waffles.zip ./
rm -rf ./package
