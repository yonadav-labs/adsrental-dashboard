<?php

	ini_set('display_errors', 1);

	require_once(__DIR__ . "/../include/config.php");
	require_once(__DIR__ . "/../include/salesforce.inc");

	require_once(__DIR__ . "/../include/jsonhelpers.inc");
	
	function getUSPSTrackingInfo($trackingNumber)
	{
		$xml = urlencode("<TrackRequest USERID=\"039ADCRU4974\"><TrackID ID=\"$trackingNumber\"></TrackID></TrackRequest>");
		$url = "https://secure.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=$xml";
		
		//echo $url;
		
		return get($url);
	}
	
	$SFData = json_decode(file_get_contents("../SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];	

	$result = getSFQueryResult("SELECT Name, USPS_Tracking_Code__c FROM Raspberry_Pi__c WHERE USPS_Tracking_Code__c != ''")["records"];

	foreach ($result as $row)
	{
		$xmlResult = getUSPSTrackingInfo($row["USPS_Tracking_Code__c"]);
		
		$parsedXML = new SimpleXMLElement($xmlResult);
		
		$lastTrackSummaryItem = (string)$parsedXML->TrackInfo[0]->TrackSummary;
		$delivered = strpos($lastTrackSummaryItem, "delivered") !== false ? true : false;
		
		createOrUpdateSFObject("Raspberry_Pi__c", "Name", $row["Name"], array("USPS_Feedback__c" => $lastTrackSummaryItem, "Delivered_Internal__c" => $delivered));
	}

?>