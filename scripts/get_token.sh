#!/bin/bash

ROOT_URL=http://localhost:8007

USER=${2:-admin@email.com}
PASSWORD=${3:-pass1234}

# echo ROOT_URL: ${ROOT_URL}

curl -XPOST ${ROOT_URL}/login/ -d "username=${USER}&password=${PASSWORD}" > /tmp/response
API_TOKEN=$(venv/bin/python -c 'import json; print json.loads(open("/tmp/response").read())["token"]')
echo "-H 'Authorization: Token ${API_TOKEN}'"
