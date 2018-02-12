#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH


if [ ! -d "venv" ]; then
    virtualenv venv
fi

sudo apt install python-qt4

source venv/bin/activate
pip install flake8==3.4.1 autopep8==1.3.3 rdpy==1.3.2
pip install -r requirements.txt
ln -s /usr/lib/python2.7/dist-packages/PyQt4/ venv/lib/python2.7/site-packages/
