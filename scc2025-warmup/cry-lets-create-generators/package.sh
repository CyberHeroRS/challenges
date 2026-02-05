set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "cry_lets_create_generators.zip" ]; then
    rm cry_lets_create_generators.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cp -r ./public/* ./package/
rm -rf ./package/hidden.py
cd ./package
zip -r cry_lets_create_generators.zip .
cd ..
mv ./package/cry_lets_create_generators.zip ./cry_lets_create_generators.zip 
rm -rf ./package
