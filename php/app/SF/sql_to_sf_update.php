<?php

	ini_set('display_errors', 1);

	require_once(__DIR__ . "/../include/config.php");
	require_once(__DIR__ . "/../include/salesforce.inc");
	require_once(__DIR__ . "/../include/mysql.inc");
	
	$SFData = json_decode(file_get_contents("../SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];	

	$rows = mysqlSelectAllRaspberryPis();
	
	foreach ($rows as $row)
	{
		$firstSeen = new DateTime($row["first_seen"], new DateTimeZone("America/Los_Angeles"));
		$lastSeen = new DateTime($row["last_seen"], new DateTimeZone("America/Los_Angeles"));
		$tunnelLastTested = new DateTime($row["tunnel_last_tested"], new DateTimeZone("America/Los_Angeles"));
		
		createOrUpdateSFObject("Raspberry_Pi__c", "Name", $row["rpid"], array(
			"First_Seen__c" => $firstSeen->format("c"),
			"Last_Seen__c" => $lastSeen->format("c"),
			"Tunnel_Last_Tested__c" => $tunnelLastTested->format("c"),
			"Current_IP_Address__c" => $row["ipaddress"]
		));
	}
	
?>