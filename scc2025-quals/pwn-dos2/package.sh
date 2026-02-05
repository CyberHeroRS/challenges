set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-dos2.zip" ]; then
    rm pwn-dos2.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r pwn-dos2.zip .
cd ..
mv ./package/pwn-dos2.zip ./pwn-dos2.zip 
rm -rf ./package
