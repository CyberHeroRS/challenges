set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-storage.zip" ]; then
    rm -f ./public/pwn-storage.zip
fi
mkdir ./package
cp ./source/storage ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn-storage.zip .
cd ..
mv ./package/pwn-storage.zip ./public/pwn-storage.zip
rm -rf ./package
