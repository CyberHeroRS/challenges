set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn-beus-levelx.zip" ]; then
    rm -f ./public/pwn-beus-levelx.zip
fi
mkdir ./package
cp ./source/beusX ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cp -r ./source/glibc ./package/
cd ./package
zip -r pwn-beus-levelx.zip .
cd ..
mv ./package/pwn-beus-levelx.zip ./public/pwn-beus-levelx.zip
rm -rf ./package
