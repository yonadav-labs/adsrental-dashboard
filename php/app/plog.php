<?php

	ini_set('display_errors', 1);
	
	require_once("include/config.php");
	require_once("include/salesforce.inc");
	require_once("include/loghelpers.inc");
	require_once("include/jsonhelpers.inc");
	
	require_once("include/AWSSDK/aws-autoloader.php");
	require_once("include/ec2helpers.inc");	

	header("Expires: Mon, 01 Jan 1985 05:00:00 GMT");
	header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
	header("Cache-Control: no-store, no-cache, must-revalidate");
	header("Cache-Control: post-check=0, pre-check=0, max-age=0", false);
	header("Pragma: no-cache");

	function nowSFFormat()
	{
		return date("Y-m-d") . "T" . date("h:m:s.000O");
	}

	$SFData = json_decode(file_get_contents("SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];

	if (!array_key_exists("uid", $_GET) || empty($_GET["uid"]))
	{
		exit;
	}

	$lead = getSFQueryResult("SELECT Id, Winprox_EC2_Instance__r.Name, Winprox_EC2_Instance__r.Hostname__c FROM Lead WHERE Winprox_UID__c = '$_GET[uid]'")["records"];

	try {
		updateSFObject("Lead", $lead[0]["Id"], array("Winprox_Last_Seen__c" => getTodayLA()->format("c")));
	} catch (\Exception $e) {
	}

	if (array_key_exists("m", $_GET))
	{
		logEntry($_GET["uid"], "Client >>> " . $_GET["m"]);
	}
	else if (array_key_exists("h", $_GET))
	{
		logEntry($_GET["uid"], "Get EC2 Instance");

		if (sizeof($lead) > 0)
		{
			$lead = $lead[0];
			//echo $lead["Winprox_EC2_Instance__r"]["Hostname__c"];

			$ec2Client = getEC2Client();
			
			// Find EC2 instances
			$result = $ec2Client->DescribeInstances(array(
					"Filters" => array(
							array("Name" => "tag:Name", "Values" => array($lead["Winprox_EC2_Instance__r"]["Name"]))
					)
			));
			
			echo $result["Reservations"][0]["Instances"][0]["PublicDnsName"];
		}
	}
	else if (array_key_exists("o", $_GET))
	{
		logEntry($_GET["uid"], "Lead online");

		updateSFObject("Lead", $lead[0]["Id"], array("Winprox_Tunnel_Last_Started__c" => getTodayLA()->format("c")));
	}
	else if (array_key_exists("m", $_POST))
	{
		$messages = explode("|", $_POST["m"]);

		foreach ($messages as $message)
		{
			logEntry($_GET["uid"], "Client >>> " . $message);
		}
	}

?>