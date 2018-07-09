#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv -p /usr/bin/python3.6
fi

source venv/bin/activate
pip install -U pip pylint autopep8 rope pylint_django --upgrade-strategy=eager
cat requirements.txt | awk 'BEGIN{FS="=="}{print $1}' > requirements_temp.txt
pip install -U -r requirements_temp.txt --upgrade-strategy=eager
rm requirements_temp.txt
