#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

python manage.py loaddata v1/fixtures/fixtures.json
