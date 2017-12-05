<?php

	require_once("include/AWSSDK/aws-autoloader.php");
	require_once("include/ec2helpers.inc");
	
	$ec2Client = getEC2Client();

	// Find EC2 instances
	$result = $ec2Client->DescribeInstances(array(
			"Filters" => array(
					array("Name" => "tag:Name", "Values" => array($_GET["h"]))
			)
	));

    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename=' . $_GET["i"] . ".rdp");
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');

	echo "auto connect:i:1\n";
	echo "full address:s:" . $result["Reservations"][0]["Instances"][0]["PublicDnsName"] . ":23255\n";
	echo "username:s:Administrator\n";
	echo "password:s:Dk.YDq8pXQS-R5ZAn84Lgma9rFvGlfvL\n";

    exit;

?>