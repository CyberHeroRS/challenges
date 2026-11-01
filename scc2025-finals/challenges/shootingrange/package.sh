set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-shootingrange.zip" ]; then
    rm -f ./public/pwn-shootingrange.zip
fi
mkdir ./package
cp ./source/app ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cp ./source/libc.so.6 ./package/
cd ./package
zip -r pwn-shootingrange.zip .
cd ..
mv ./package/pwn-shootingrange.zip ./public/pwn-shootingrange.zip
rm -rf ./package
