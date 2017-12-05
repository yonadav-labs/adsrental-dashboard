<?php

	ini_set('display_errors', 1);

	require_once(__DIR__ . "/../include/config.php");
	require_once(__DIR__ . "/../include/salesforce.inc");

	require_once(__DIR__ . "/../include/AWSSDK/aws-autoloader.php");
	require_once(__DIR__ . "/../include/ec2helpers.inc");

	// Get all leads w/o AWS Instance Proxy set and browser extension status != uninstalled

	$ec2Client = getEC2Client();

	$SFData = json_decode(file_get_contents(__DIR__ . "/../SF.json"), true);

	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];

	$sfQuery = "SELECT Id, Name FROM EC2_Instance__c WHERE Hostname__c = '' AND Instance_ID__c != ''";

	$sfResult = getSFQueryResult($sfQuery)["records"];

	foreach ($sfResult as $row)
	{
		// Find EC2 instances
		$result = $ec2Client->DescribeInstances(array(
		        "Filters" => array(
		                array("Name" => "tag:Name", "Values" => array($row["Name"]))
		        )
		));

		echo $result["Reservations"][0]["Instances"][0]["PublicDnsName"];

		updateSFObject("EC2_Instance__c", $row["Id"], array("Hostname__c" => $result["Reservations"][0]["Instances"][0]["PublicDnsName"]));

		echo "-----------------------------------------------------\n";
	}

?>