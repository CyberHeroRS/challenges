set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/cry_cards_act_ii.zip" ]; then
    rm -f ./public/cry_cards_act_ii.zip
fi
mkdir ./package
cp -r ./source/* ./package/
zip -r ./public/cry_cards_act_ii.zip ./package
rm -rf ./package
