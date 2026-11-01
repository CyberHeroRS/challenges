set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-aop1.zip" ]; then
    rm -f ./public/pwn-aop1.zip
fi
mkdir ./package
cp ./source/aop1 ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cp -r ./source/glibc ./package/
cd ./package
zip -r pwn-aop1.zip .
cd ..
mv ./package/pwn-aop1.zip ./public/pwn-aop1.zip
rm -rf ./package
