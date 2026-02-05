set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-storage.zip" ]; then
    rm pwn-storage.zip
fi
mkdir ./package
cp ./source/storage ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn-storage.zip .
cd ..
mv ./package/pwn-storage.zip ./pwn-storage.zip 
rm -rf ./package