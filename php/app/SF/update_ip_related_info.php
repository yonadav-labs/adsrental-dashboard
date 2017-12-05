<?php

	if (!array_key_exists("rpid", $_GET) || !array_key_exists("ipaddress", $_GET))
	{
		exit;
	}
	
	ini_set('display_errors', 1);
	
	require_once("../include/config.php");
	require_once("../include/salesforce.inc");
	require_once("../include/loghelpers.inc");
	require_once("../include/jsonhelpers.inc");
	require_once("../include/iphelpers.inc");

	$SFData = json_decode(file_get_contents("../SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];
	
	$ipInfo = getIPInfo($_GET["ipaddress"]);
	
	//print_r($ipInfo);
	
	createOrUpdateSFObject("Raspberry_Pi__c", "Name", $_GET["rpid"], array("Current_ISP__c" => $ipInfo["isp"], "Current_City__c" => $ipInfo["city"], "Current_State_Region__c" => $ipInfo["regionName"], "Current_Country__c" => $ipInfo["countryCode"]));
	
?>