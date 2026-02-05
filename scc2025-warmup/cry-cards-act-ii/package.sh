set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "cry_cards_act_ii.zip" ]; then
    rm cry_cards_act_ii.zip
fi
mkdir ./package
cp -r ./source/* ./package/
zip -r cry_cards_act_ii.zip ./package 
rm -rf ./package
