set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-strcatenator.zip" ]; then
    rm -f ./public/pwn-strcatenator.zip
fi
mkdir ./package
cp ./source/chall/app ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cp ./source/strcatenator.pas ./package/
cd ./package
zip -r pwn-strcatenator.zip .
cd ..
mv ./package/pwn-strcatenator.zip ./public/pwn-strcatenator.zip
rm -rf ./package
