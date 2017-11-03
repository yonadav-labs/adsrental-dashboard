#!/bin/bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

docker build .
docker commit $(docker ps -lq) adsrental

docker login http://vlad:adsinc@165.227.74.143:5043
docker push 165.227.74.143:5043/adsrental