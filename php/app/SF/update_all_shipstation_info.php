<?php

	ini_set('display_errors', 1);

	require_once(__DIR__ . "/../include/config.php");
	require_once(__DIR__ . "/../include/salesforce.inc");

	require_once(__DIR__ . "/../include/jsonhelpers.inc");
	
	function getUSPSTrackingNumber($accountNumber)
	{
		return getBasicAuthenticationJSON("https://ssapi.shipstation.com/shipments?orderNumber=$accountNumber", "483e019cf2244e9484a98c913e8691b0", "4903c001173546828752c30887c9b3f9");
	}

	$SFData = json_decode(file_get_contents("../SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];	

	$result = getSFQueryResult("SELECT Name, Linked_Lead__r.Account_Name__c FROM Raspberry_Pi__c WHERE USPS_Tracking_Code__c = '' AND Linked_Lead__r.Account_Name__c != ''")["records"];

	foreach ($result as $row)
	{
		$json = getUSPSTrackingNumber($row["Linked_Lead__r"]["Account_Name__c"]);
		
		print_r($json);
		print_r($row);
		
		if ($json != null && sizeof($json["shipments"] > 0) && !empty($json["shipments"][0]["trackingNumber"]))
		{
			createOrUpdateSFObject("Raspberry_Pi__c", "Name", $row["Name"], array("USPS_Tracking_Code__c" => $json["shipments"][0]["trackingNumber"]));
			
			echo "Updated " . $row["Linked_Lead__r"]["Account_Name__c"] . ": " . $json["shipments"][0]["trackingNumber"] . ".\n";
		}
	}
	
?>