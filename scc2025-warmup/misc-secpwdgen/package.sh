set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "misc_secpwdgen.zip" ]; then
    rm misc_secpwdgen.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r misc_secpwdgen.zip .
cd ..
mv ./package/misc_secpwdgen.zip ./misc_secpwdgen.zip 
rm -rf ./package
