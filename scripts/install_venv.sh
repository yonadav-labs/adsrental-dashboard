#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv -p /usr/bin/python3.6
fi

source venv/bin/activate
pip install -U pip rope --upgrade-strategy=eager
pip install git+https://github.com/PyCQA/pylint.git
pip install git+https://github.com/PyCQA/pylint-django.git
cat requirements.txt | awk 'BEGIN{FS="=="}{print $1}' > requirements_temp.txt
pip install -U -r requirements_temp.txt --upgrade-strategy=eager
rm requirements_temp.txt
