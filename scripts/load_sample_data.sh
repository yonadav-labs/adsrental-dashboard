#!/bin/bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH
source venv/bin/activate
python manage.py loaddata v1/fixtures/fixtures.json
