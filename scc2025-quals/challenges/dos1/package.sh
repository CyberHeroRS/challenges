set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-dos1.zip" ]; then
    rm -f ./public/pwn-dos1.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r pwn-dos1.zip .
cd ..
mv ./package/pwn-dos1.zip ./public/pwn-dos1.zip
rm -rf ./package
