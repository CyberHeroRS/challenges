set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-strcatenator.zip" ]; then
    rm pwn-strcatenator.zip
fi
mkdir ./package
cp ./src/chall/app ./package/
cp ./src/Dockerfile ./package/
cp ./src/docker-compose.yml ./package/
cp ./src/strcatenator.pas ./package/
cd ./package
zip -r pwn-strcatenator.zip .
cd ..
mv ./package/pwn-strcatenator.zip ./pwn-strcatenator.zip 
rm -rf ./package
