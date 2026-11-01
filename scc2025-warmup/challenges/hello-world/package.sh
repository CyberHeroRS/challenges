set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/welcome_hello_world.zip" ]; then
    rm -f ./public/welcome_hello_world.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r welcome_hello_world.zip .
cd ..
mv ./package/welcome_hello_world.zip ./public/welcome_hello_world.zip
rm -rf ./package
