<?php

ini_set('display_errors', 1);

	require_once(__DIR__ . "/../include/config.php");
	require_once(__DIR__ . "/../include/salesforce.inc");

	require_once(__DIR__ . "/../include/AWSSDK/aws-autoloader.php");
	require_once(__DIR__ . "/../include/ec2helpers.inc");

	$SFData = json_decode(file_get_contents(__DIR__ . "/../SF.json"), true);

	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];	

    $ec2Client = getEC2Client();
    $rpid = $_GET["rpid"];
    $ec2Result = launchRASPIInstance($ec2Client, $rpid);
	$ec2InstanceId = createSFObject("EC2_Instance__c", array("Name" => $_GET["rpid"], "Instance_ID__c" => $ec2Result["Instances"][0]["InstanceId"]));
    echo "$rpid launched";
?>
