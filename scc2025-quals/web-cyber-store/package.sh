set -e
if [ -d "./package" ]; then
  rm -rf ./package
fi

if [ -f "web-cyber-store.zip" ]; then
  rm -f web-cyber-store.zip
fi

mkdir ./package
cp -r ./source/* ./package/
cd ./package
rm -rf node_modules public
zip -r web-cyber-store.zip .
cd ..
mv ./package/web-cyber-store.zip ./
rm -rf ./package
