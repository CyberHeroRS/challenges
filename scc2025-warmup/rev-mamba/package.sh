set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "rev_mamba.zip" ]; then
    rm rev_mamba.zip
fi
mkdir ./package
cp ./public/* ./package/
cd ./package
zip -r rev_mamba.zip .
cd ..
mv ./package/rev_mamba.zip ./rev_mamba.zip 
rm -rf ./package
