set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/forensics_secret_archives.zip" ]; then
    rm -f ./public/forensics_secret_archives.zip
fi
mkdir ./package
cp -r ./source/* ./package/
rm -rf ./package/flag.png
cd ./package
zip -r forensics_secret_archives.zip .
cd ..
mv ./package/forensics_secret_archives.zip ./public/forensics_secret_archives.zip
rm -rf ./package
