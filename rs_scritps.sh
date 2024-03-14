#!/bin/bash


#screen -S test

echo "$(date +"%Y-%m-%d %T") Current directory: $(pwd)"

#echo "createing the build"
#sudo docker build -t recsys .cho "build is ready runing docker"
echo "$(date +"%Y-%m-%d %T") running the image"
sudo docker run recsys 

screen -dS test 