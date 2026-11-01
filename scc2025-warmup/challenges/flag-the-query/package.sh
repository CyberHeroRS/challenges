set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web_flag_the_query.zip" ]; then
    rm -f ./public/web_flag_the_query.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_flag_the_query.zip .
cd ..
mv ./package/web_flag_the_query.zip ./public/web_flag_the_query.zip
rm -rf ./package
