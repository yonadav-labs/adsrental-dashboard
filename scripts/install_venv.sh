#!/bin/bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv
fi

source venv/bin/activate
pip install -U pip
pip install -r requirements/base.txt
