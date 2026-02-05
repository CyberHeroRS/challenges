set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "welcome_hello_world.zip" ]; then
    rm welcome_hello_world.zip
fi
mkdir ./package
cp -r ./public/* ./package/
cd ./package
zip -r welcome_hello_world.zip .
cd ..
mv ./package/welcome_hello_world.zip ./welcome_hello_world.zip 
rm -rf ./package
