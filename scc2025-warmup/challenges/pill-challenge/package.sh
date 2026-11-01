set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web_pill_challenge.zip" ]; then
    rm -f ./public/web_pill_challenge.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_pill_challenge.zip .
cd ..
mv ./package/web_pill_challenge.zip ./public/web_pill_challenge.zip
rm -rf ./package
