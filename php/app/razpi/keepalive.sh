#!/bin/bash

if [ $# -eq 0 ]
	then
		echo "No arguments supplied to keepalive"
		exit
fi

RaspberryPiID=$1

echo "Starting continuous ping for $RaspberryPiID..."

while true
do
	echo "Ping"
	curl "https://adsrental.com/rlog.php?rpid=$RaspberryPiID&p"
	sleep 1m
done