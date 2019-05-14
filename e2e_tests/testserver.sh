#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH


# echo "=== Starting server ==="
docker-compose -f docker-compose.test.yml up -d --build web

./scripts/wait-for-it.sh localhost:23306

echo "=== Installing test DB ==="
mysql -u root -h 0.0.0.0 -P 23306 -e 'drop database if exists adsrental_test;'
mysql -u root -h 0.0.0.0 -P 23306 -e 'create database adsrental_test;'
zcat e2e_tests/test.sql.gz | mysql -u root -h 0.0.0.0 -P 23306 adsrental_test
