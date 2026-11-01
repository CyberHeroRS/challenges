set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn_cards.zip" ]; then
    rm -f ./public/pwn_cards.zip
fi
mkdir ./package
cp ./source/chal ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_cards.zip .
cd ..
mv ./package/pwn_cards.zip ./public/pwn_cards.zip
rm -rf ./package
