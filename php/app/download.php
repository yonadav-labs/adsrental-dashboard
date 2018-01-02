<?php

	ini_set('display_errors', 1);
	
	if (!array_key_exists("uid", $_GET) || empty($_GET["uid"]))
	{
		exit;
	}

	require_once(__DIR__ . "/include/loghelper.inc");
	require_once(__DIR__ . "/include/jsonhelpers.inc");
	require_once(__DIR__ . "/include/iphelpers.inc");

	if (isFacebookASN($_SERVER["REMOTE_ADDR"]))
	{
		logEntry($_GET["uid"], "Facebook IP Detected. Exiting.");
		exit;
	}

	require_once(__DIR__ . "/include/config.php");
	require_once(__DIR__ . "/include/salesforce.inc");

	require_once(__DIR__ . "/include/AWSSDK/aws-autoloader.php");
	require_once(__DIR__ . "/include/ec2helpers.inc");

	$SFData = json_decode(file_get_contents(__DIR__ . "/SF.json"), true);

	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];

	logEntry($_GET["uid"], "Download winprox");

	$ec2Client = getEC2Client();

	$leadResult = getSFQueryResult("SELECT Id, Winprox_EC2_Instance__c FROM Lead WHERE Winprox_UID__c = '$_GET[uid]'")["records"][0];

	$leadId = $leadResult["Id"];

	$updatedLeadFields = array("Winprox_Status__c" => "Downloaded");

	if ($leadResult["Winprox_EC2_Instance__c"] == null)
	{
		$oldestAvailableEC2Instance = getSFQueryResult("select Id, Name FROM EC2_Instance__c WHERE Id NOT IN (SELECT winprox_ec2_Instance__c FROM Lead) ORDER By Name ASC LIMIT 1")["records"][0];
		logEntry($_GET["uid"], "Assigning EC2 insstance: " . $oldestAvailableEC2Instance["Id"]);

		$updatedLeadFields["Winprox_EC2_Instance__c"] = $oldestAvailableEC2Instance["Id"];

		$ec2InstanceId = launchWINPROXInstance($ec2Client);

		logEntry($_GET["uid"], "Created EC2 Instance: " . $ec2InstanceId);		
	}

	updateSFObject("Lead", $leadId, $updatedLeadFields);

	$filename = "AdsRental_" . $_GET["uid"] . ".exe";

	header("Content-Type: application/vnd.microsoft.portable-executable");

	header("Content-Disposition: attachment; filename=$filename");

	readfile("AdsRental.exe");

?>