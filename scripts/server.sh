#!/bin/bash
ROOT_PATH=$(dirname $(dirname $0))
cd $ROOT_PATH

source venv/bin/activate

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8007 \
    --workers 3
   --timeout 300

