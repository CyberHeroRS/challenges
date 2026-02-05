set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn-dos1.zip" ]; then
    rm pwn-dos1.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r pwn-dos1.zip .
cd ..
mv ./package/pwn-dos1.zip ./pwn-dos1.zip 
rm -rf ./package
