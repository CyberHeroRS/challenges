set -e
mkdir -p ./public
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "./public/pwn_maze_simulation.zip" ]; then
    rm -f ./public/pwn_maze_simulation.zip
fi
mkdir ./package
cp ./source/chal ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_maze_simulation.zip .
cd ..
mv ./package/pwn_maze_simulation.zip ./public/pwn_maze_simulation.zip
rm -rf ./package
