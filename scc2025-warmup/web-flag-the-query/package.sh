set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "web_flag_the_query.zip" ]; then
    rm web_flag_the_query.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_flag_the_query.zip .
cd ..
mv ./package/web_flag_the_query.zip ./web_flag_the_query.zip 
rm -rf ./package
