function init
{
	echo "Getting config data"

	if [ -e /boot/pi.conf ]
	then
		echo "Using /boot/pi.conf"
		RaspberryPiID=$(echo -n `cat /boot/pi.conf`)
	else
		echo "Using pi.conf"
		RaspberryPiID=$(echo -n `cat pi.conf`)
	fi

	echo "RaspberryPiID: $RaspberryPiID"

	EC2Instance=$(curl -f -H "Accept: application/json" -H "Content-Type: application/json" "https://adsrental.com/rlog.php?rpid=$RaspberryPiID&h")

	# Retry until we get our hostname
	until [ ! -z "${EC2Instance// }" ]
	do
		echo "Getting EC2 Instance";
		EC2Instance=$(curl -f -H "Accept: application/json" -H "Content-Type: application/json" "https://adsrental.com/rlog.php?rpid=$RaspberryPiID&h")
		sleep 30
	done
}