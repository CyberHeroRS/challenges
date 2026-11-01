set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/rev_mamba.zip" ]; then
    rm -f ./public/rev_mamba.zip
fi
mkdir ./package
cp ./public/* ./package/
cd ./package
zip -r rev_mamba.zip .
cd ..
mv ./package/rev_mamba.zip ./public/rev_mamba.zip
rm -rf ./package
