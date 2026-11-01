set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/misc_secpwdgen.zip" ]; then
    rm -f ./public/misc_secpwdgen.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r misc_secpwdgen.zip .
cd ..
mv ./package/misc_secpwdgen.zip ./public/misc_secpwdgen.zip
rm -rf ./package
