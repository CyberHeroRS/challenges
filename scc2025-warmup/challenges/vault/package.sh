set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/rev_vault.zip" ]; then
    rm -f ./public/rev_vault.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r rev_vault.zip .
cd ..
mv ./package/rev_vault.zip ./public/rev_vault.zip
rm -rf ./package
