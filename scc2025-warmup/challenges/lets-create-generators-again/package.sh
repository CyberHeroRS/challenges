set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/cry_lets_create_generators_again.zip" ]; then
    rm -f ./public/cry_lets_create_generators_again.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cp -r ./public/* ./package/
rm -rf ./package/hidden.py
cd ./package
zip -r cry_lets_create_generators_again.zip .
cd ..
mv ./package/cry_lets_create_generators_again.zip ./public/cry_lets_create_generators_again.zip
rm -rf ./package
