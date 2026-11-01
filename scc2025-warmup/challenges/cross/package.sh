set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web_croSS.zip" ]; then
    rm -f ./public/web_croSS.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_croSS.zip .
cd ..
mv ./package/web_croSS.zip ./public/web_croSS.zip
rm -rf ./package
