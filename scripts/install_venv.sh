#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv -p /usr/bin/python3.6
fi

source venv/bin/activate
pip install flake8==3.5.0 autopep8==1.3.4
pip install -U -r requirements.txt
