set -e
mkdir -p ./public
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "./public/web-waffles.zip" ]; then
    rm -f ./public/web-waffles.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
rm -rf waf/target
zip -r web-waffles.zip .
cd ..
mv ./package/web-waffles.zip ./public/web-waffles.zip
rm -rf ./package
