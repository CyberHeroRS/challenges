set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web_len5.zip" ]; then
    rm -f ./public/web_len5.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_len5.zip .
cd ..
mv ./package/web_len5.zip ./public/web_len5.zip
rm -rf ./package
