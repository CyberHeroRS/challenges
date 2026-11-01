set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/web_im_a_spy_ama.zip" ]; then
    rm -f ./public/web_im_a_spy_ama.zip
fi
mkdir ./package
cp -r ./source/* ./package/
cd ./package
zip -r web_im_a_spy_ama.zip .
cd ..
mv ./package/web_im_a_spy_ama.zip ./public/web_im_a_spy_ama.zip
rm -rf ./package
