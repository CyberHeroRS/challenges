set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn_fancy_restaurant.zip" ]; then
    rm pwn_fancy_restaurant.zip
fi
mkdir ./package
cp ./source/fancy ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_fancy_restaurant.zip .
cd ..
mv ./package/pwn_fancy_restaurant.zip ./pwn_fancy_restaurant.zip 
rm -rf ./package
