#!/bin/bash

. ./lib.sh

init

while read line; do
    echo "LOG: $line"																			#stdout
    echo $line >> pi.log 																		#file
    curl -G "https://adsrental.com/rlog.php?rpid=$RaspberryPiID" --data-urlencode "m=$line"		#server
done