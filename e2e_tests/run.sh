#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $(realpath $0)))
cd $ROOT_PATH


# echo "=== Starting server ==="
# docker-compose -f docker-compose.test.yml up web


echo "=== Installing test DB ==="
mysql -u root -h 0.0.0.0 -P 23306 -e 'create database if not exists adsrental_test;'
zcat e2e_tests/test.sql.gz | mysql -u root -h 0.0.0.0 -P 23306 adsrental_test

echo "=== Running tests $1 ==="
cd e2e_tests
npx codeceptjs run --steps --grep "$1"
cd -

# echo "=== Stopping server ==="
# docker-compose down
