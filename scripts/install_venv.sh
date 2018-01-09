#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv
fi

source venv/bin/activate
pip install flake8==3.4.1 autopep8==1.3.3
pip install -r requirements/base.txt
