set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "forensics_secret_archives.zip" ]; then
    rm forensics_secret_archives.zip
fi
mkdir ./package
cp -r ./source/* ./package/
rm -rf ./package/flag.png
cd ./package
zip -r forensics_secret_archives.zip .
cd ..
mv ./package/forensics_secret_archives.zip ./forensics_secret_archives.zip
rm -rf ./package
