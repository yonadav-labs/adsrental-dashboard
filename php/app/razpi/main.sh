#!/bin/bash

. ./lib.sh

function startKeepalive
{
	echo "startKeepalive"

	exec ./keepalive.sh $RaspberryPiID &
}

function startSSH
{
	echo "startSSH"

	autossh -f -nNT -oStrictHostKeyChecking=no -R 2046:localhost:16777 -p 40594 Administrator@$EC2Instance # change to autossh
}

function signalReverseTunnel
{
	echo "signalReverseTunnel"

	resultOutput=$(curl "http://$EC2Instance:13608/start-tunnel")

	echo $resultOutput
}

# Wait until network is up
until ping -c1 adsrental.com &>/dev/null; do :; done

echo "============================================================================================================================"

init
echo "AFTER INIT: $RaspberryPiID : $EC2Instance"
ip addr show

startKeepalive

startSSH

echo "Waiting 1 minute"
sleep 1m

signalReverseTunnel

echo "============================================================================================================================"

#dos2unix main.sh
#schedule daily reboot of pis
