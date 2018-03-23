#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv -p /usr/bin/python3.6
fi

source venv/bin/activate
pip install pylint autopep8 rope
pip install -U -r requirements.txt
