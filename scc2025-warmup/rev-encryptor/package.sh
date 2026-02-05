set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "rev_encryptor.zip" ]; then
    rm rev_encryptor.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r rev_encryptor.zip .
cd ..
mv ./package/rev_encryptor.zip ./rev_encryptor.zip 
rm -rf ./package
