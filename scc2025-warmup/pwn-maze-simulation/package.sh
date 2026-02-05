set -e
if [ -d "./package" ]; then
    rm -rf ./package
fi
if [ -f "pwn_maze_simulation.zip" ]; then
    rm pwn_maze_simulation.zip
fi
mkdir ./package
cp ./source/chal ./package/
cp ./source/Dockerfile ./package/
cp ./source/docker-compose.yml ./package/
cd ./package
zip -r pwn_maze_simulation.zip .
cd ..
mv ./package/pwn_maze_simulation.zip ./pwn_maze_simulation.zip 
rm -rf ./package
