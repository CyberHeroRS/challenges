set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "cry_gods_and_monsters.zip" ]; then
    rm cry_gods_and_monsters.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cp -r ./public/* ./package/
rm -rf ./package/hidden.py
cd ./package
zip -r cry_gods_and_monsters.zip .
cd ..
mv ./package/cry_gods_and_monsters.zip ./cry_gods_and_monsters.zip 
rm -rf ./package
