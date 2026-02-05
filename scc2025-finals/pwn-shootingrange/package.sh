set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-shootingrange.zip" ]; then
    rm pwn-shootingrange.zip
fi
mkdir ./package
cp ./source/app ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cp ./source/libc.so.6 ./package/
cd ./package
zip -r pwn-shootingrange.zip .
cd ..
mv ./package/pwn-shootingrange.zip ./pwn-shootingrange.zip 
rm -rf ./package
