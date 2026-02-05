set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn_beus_level1.zip" ]; then
    rm pwn_beus_level1.zip
fi
mkdir ./package
cp ./source/beus1 ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_beus_level1.zip .
cd ..
mv ./package/pwn_beus_level1.zip ./pwn_beus_level1.zip 
rm -rf ./package
