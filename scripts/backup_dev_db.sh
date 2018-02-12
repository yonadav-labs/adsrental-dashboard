#!/usr/bin/env bash

mysqldump -h 0.0.0.0 -P 13306 adsrental | gzip > /mnt/volume-nyc3-01/mysqldumps/dump_`date +%Y_%m_%d`.sql.gz
