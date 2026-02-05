set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "web_len5.zip" ]; then
    rm web_len5.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_len5.zip .
cd ..
mv ./package/web_len5.zip ./web_len5.zip 
rm -rf ./package
