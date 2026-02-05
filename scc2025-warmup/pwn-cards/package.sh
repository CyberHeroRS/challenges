set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn_cards.zip" ]; then
    rm pwn_cards.zip
fi
mkdir ./package
cp ./source/chal ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_cards.zip .
cd ..
mv ./package/pwn_cards.zip ./pwn_cards.zip 
rm -rf ./package
