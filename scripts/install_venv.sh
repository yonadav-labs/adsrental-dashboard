#!/bin/bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv
fi

source venv/bin/activate
rm /usr/local/bin/python
ln -s /app/venv/bin/python /usr/local/bin/python
pip install -r requirements/base.txt
