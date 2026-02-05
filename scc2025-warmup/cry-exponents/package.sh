set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "cry_exponents.zip" ]; then
    rm cry_exponents.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cp -r ./public/* ./package/
rm -rf ./package/hidden.py
cd ./package
zip -r cry_exponents.zip .
cd ..
mv ./package/cry_exponents.zip ./cry_exponents.zip 
rm -rf ./package
