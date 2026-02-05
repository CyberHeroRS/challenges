set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "web_pill_challenge.zip" ]; then
    rm web_pill_challenge.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_pill_challenge.zip .
cd ..
mv ./package/web_pill_challenge.zip ./web_pill_challenge.zip 
rm -rf ./package
