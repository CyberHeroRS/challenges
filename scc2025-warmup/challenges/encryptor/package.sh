set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/rev_encryptor.zip" ]; then
    rm -f ./public/rev_encryptor.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r rev_encryptor.zip .
cd ..
mv ./package/rev_encryptor.zip ./public/rev_encryptor.zip
rm -rf ./package
