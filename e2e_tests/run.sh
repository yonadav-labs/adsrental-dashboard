#!/usr/bin/env bash

# docker-compose up --build web
npx codeceptjs run --steps --grep "$1"
