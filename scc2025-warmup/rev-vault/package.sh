set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "rev_vault.zip" ]; then
    rm rev_vault.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r rev_vault.zip .
cd ..
mv ./package/rev_vault.zip ./rev_vault.zip 
rm -rf ./package
