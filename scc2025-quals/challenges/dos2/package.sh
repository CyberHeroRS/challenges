set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-dos2.zip" ]; then
    rm -f ./public/pwn-dos2.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r pwn-dos2.zip .
cd ..
mv ./package/pwn-dos2.zip ./public/pwn-dos2.zip
rm -rf ./package
