set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web-spyMe.zip" ]; then
    rm -f ./public/web-spyMe.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web-spyMe.zip .
cd ..
mv ./package/web-spyMe.zip ./public/web-spyMe.zip
rm -rf ./package
