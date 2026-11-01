set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn_beus_level2.zip" ]; then
    rm -f ./public/pwn_beus_level2.zip
fi
mkdir ./package
cp ./source/beus2 ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_beus_level2.zip .
cd ..
mv ./package/pwn_beus_level2.zip ./public/pwn_beus_level2.zip
rm -rf ./package
