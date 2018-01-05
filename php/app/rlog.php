<?php

	ini_set('display_errors', 1);

	require_once("include/config.php");
	require_once("include/salesforce.inc");
	require_once("include/loghelper.inc");
	require_once("include/jsonhelpers.inc");

	require_once("include/AWSSDK/aws-autoloader.php");
	require_once("include/ec2helpers.inc");

	require_once("include/mysql.inc");
	require_once("include/slack.inc");

	// header("Content-Type: application/json");
	header("Expires: Mon, 01 Jan 1985 05:00:00 GMT");
	header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
	header("Cache-Control: no-store, no-cache, must-revalidate");
	header("Cache-Control: post-check=0, pre-check=0, max-age=0", false);
	header("Pragma: no-cache");

	function nowSFFormat()
	{
		return date("Y-m-d") . "T" . date("H:i:s.000O");
	}

	$SFData = json_decode(file_get_contents("SF.json"), true);
	$lead = null;

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];

	if (!array_key_exists("rpid", $_GET) || empty($_GET["rpid"]))
	{
		exit;
	}

	if (array_key_exists("m", $_GET))
	{
		logEntry($_GET["rpid"], "Client >>> " . $_GET["m"]);
	}
	else
	{
		/*
		try
		{
			$lead = getSFQueryResult("SELECT Id, Raspberry_Pi__c, Raspberry_Pi__r.EC2_Instance__r.Hostname__c FROM Lead WHERE Raspberry_Pi__r.Name = '$_GET[rpid]'")["records"];

			if (!array_key_exists("0", $lead))
			{
				logEntry($_GET["rpid"], "Lead not found");

				exit;
			}

			updateSFObject("Raspberry_Pi__c", $lead[0]["Raspberry_Pi__c"], array("Current_IP_Address__c" => $_SERVER["REMOTE_ADDR"], "Last_Seen__c" => getTodayLA()->format("c")));
		}
		catch (Exception $e)
		{
			logEntry($_GET["rpid"], $e->getMessage());
			exit;
		}*/

		if (mysqlUpsertRaspberryPi($_GET["rpid"]) == null)
		{
			$leads = getSFQueryResult("SELECT Id, FirstName, LastName, Email, Phone, Street, City, State, PostalCode, Country, Account_Name__c, Raspberry_Pi__r.Name, Raspberry_Pi__r.USPS_Tracking_Code__c, utm_source__c, Google_Account__c, Facebook_Account__c, Wrong_Password__c, Bundler_Paid__c, Raspberry_Pi__r.Delivered__c FROM Lead WHERE Raspberry_Pi__r.Name = '$_GET[rpid]'")["records"];

			if (!$leads){
				echo "No leads found for $_GET[rpid]";
				exit;
			}
			$lead = $leads[0];

			$leadAddress = $lead["Street"] . ", " . $lead["City"] . ", " . $lead["State"] . ", " . $lead["PostalCode"] . ", " . $lead["Country"];

			mysqlInsertLeadAndLink(
				$_GET["rpid"],
				$lead,
				$leadAddress,
				$lead["Raspberry_Pi__r"]["USPS_Tracking_Code__c"]
			);

			if ($_SERVER["REMOTE_ADDR"] != "24.234.215.233")
			{
				$slackMessage = $_GET["rpid"] . " - <https://na40.salesforce.com/$lead[Id]|" . $lead["FirstName"] . " " . $lead["LastName"] . "> is online";

				sendSlackMessage("https://hooks.slack.com/services/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", $slackMessage);
			}
		}

		// GET EC2 INSTANCE
		if (array_key_exists("h", $_GET))
		{
			logEntry($_GET["rpid"], "GET EC2 INSTANCE");
/*
			if (sizeof($lead) > 0)
			{
				$lead = $lead[0];
				echo $lead["Raspberry_Pi__r"]["EC2_Instance__r"]["Hostname__c"];
			}
*/
			$ec2Client = getEC2Client();

			// Find EC2 instances
			$result = $ec2Client->DescribeInstances(array(
					"Filters" => array(
							array("Name" => "tag:Name", "Values" => array($_GET["rpid"]))
					)
			));

			echo $result["Reservations"][0]["Instances"][0]["PublicDnsName"];
		}
		// TUNNEL ONLINE
		else if (array_key_exists("o", $_GET))
		{
			logEntry($_GET["rpid"], "TUNNEL ONLINE: " . $_SERVER["REMOTE_ADDR"]);

			//updateSFObject("Raspberry_Pi__c", $lead[0]["Raspberry_Pi__c"], array("Tunnel_Last_Tested__c" => getTodayLA()->format("c")));
			createOrUpdateSFObject("Raspberry_Pi__c", "Name", $_GET["rpid"], array("Last_Seen__c" => nowSFFormat()));
			mysqlUpsertRaspberryPi($_GET["rpid"], true);

			echo "Tunnel Online: " . $_SERVER["REMOTE_ADDR"];
		}
		// PING
		else if (array_key_exists("p", $_GET))
		{
			// logEntry($_GET["rpid"], "PING");
			// $updateFromSF = (date("i", time()) % 30 == 0) || isset($_GET['update']);
			$updateFromSF = false;
			echo "PING at " . nowSFFormat() . " from ". $_SERVER["REMOTE_ADDR"];
			if ($_SERVER["REMOTE_ADDR"] == "24.234.215.233") {
				createOrUpdateSFObject("Raspberry_Pi__c", "Name", $_GET["rpid"], array("Tested_Internal__c" => true));
			}
			if ($updateFromSF)
			{
				createOrUpdateSFObject("Raspberry_Pi__c", "Name", $_GET["rpid"], array("Last_Seen__c" => nowSFFormat()));
				$lead = getSFQueryResult(<<<EOD
					SELECT
						Id,
						FirstName,
						LastName,
						Email,
						Phone,
						Street,
						City,
						State,
						PostalCode,
						Country,
						Account_Name__c,
						Raspberry_Pi__r.USPS_Tracking_Code__c,
						utm_source__c,
						Google_Account__c,
						Facebook_Account__c,
						Wrong_Password__c,
						Bundler_Paid__c,
						Facebook_Account_Status__c,
						Google_Account_Status__c
					FROM Lead WHERE Raspberry_Pi__r.Name = '$_GET[rpid]'
EOD
				)["records"][0];
	
				$leadAddress = $lead["Street"] . ", " . $lead["City"] . ", " . $lead["State"] . ", " . $lead["PostalCode"] . ", " . $lead["Country"];
	
				mysqlInsertLeadAndLink(
					$_GET["rpid"],
					$lead,
					$leadAddress,
					$lead["Raspberry_Pi__r"]["USPS_Tracking_Code__c"]
				);
				echo "State updated\n";
			}
			// echo "Pong\n";
		}
	}

?>