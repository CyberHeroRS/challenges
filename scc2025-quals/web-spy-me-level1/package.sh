set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "web-spyMe.zip" ]; then
    rm web-spyMe.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web-spyMe.zip .
cd ..
mv ./package/web-spyMe.zip ./web-spyMe.zip
rm -rf ./package
