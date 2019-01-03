#!/usr/bin/env bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

FLAG_UPGRADE=0
FLAG_DEV=0

while [ $# -ne 0 ]
do
    arg="$1"
    case "$arg" in
        -h)
            echo "Usage: $0 [-d] [-u]"
            echo " -d --dev     Install dev dependencies"
            echo " -u --upgrade Install latest versions of dependencies"
            exit;
            ;;
        -u)
            FLAG_UPGRADE=1
            ;;
        --upgrade)
            FLAG_UPGRADE=1
            ;;
        -d)
            FLAG_DEV=1
            ;;
        --dev)
            FLAG_DEV=1
            ;;
    esac
    shift
done

if [ ! -d "venv" ]; then
    echo "* Installing virtualenv"
    virtualenv venv -p python3.7
fi

echo "* Activating virtualenv"
source venv/bin/activate
echo "* Installing latest pip"
pip install -q -U pip

if [[ $FLAG_DEV -eq 1 ]]; then
    if [[ $FLAG_UPGRADE -eq 1 ]]; then
        echo "* Installing latest requirements-dev.txt"
        cat requirements-dev.txt | awk 'BEGIN{FS="=="}{print $1}' > requirements-dev_temp.txt
        pip install -U -r requirements-dev_temp.txt --upgrade-strategy=eager
        rm requirements-dev_temp.txt
    else
        echo "* Installing requirements-dev.txt"
        pip install -U -r requirements-dev.txt --upgrade-strategy=eager
    fi
fi

if [[ $FLAG_UPGRADE -eq 1 ]]; then
    echo "* Installing latest requirements.txt"
    cat requirements.txt | awk 'BEGIN{FS="=="}{print $1}' > requirements_temp.txt
    pip install -U -r requirements_temp.txt --upgrade-strategy=eager
    rm requirements_temp.txt
else
    echo "* Installing requirements.txt"
    pip install -U -r requirements.txt --upgrade-strategy=eager
fi

echo "* Done!"
