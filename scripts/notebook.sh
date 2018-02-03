#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

python manage.py shell_plus --notebook
