set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "web_spyMe.zip" ]; then
    rm web_spyMe.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_spyMe.zip .
cd ..
mv ./package/web_spyMe.zip ./web_spyMe.zip 
rm -rf ./package
