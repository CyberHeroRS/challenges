set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-notary.zip" ]; then
    rm pwn-notary.zip
fi
mkdir ./package
cp ./source/app ./package/
cp ./source/Dockerfile ./package/
cp ./source/libc.so.6 ./package/
cp ./source/docker-compose.yml ./package/
cp ./source/ld-linux-x86-64.so.2 ./package/
cd ./package
zip -r pwn-notary.zip .
cd ..
mv ./package/pwn-notary.zip ./pwn-notary.zip 
rm -rf ./package
