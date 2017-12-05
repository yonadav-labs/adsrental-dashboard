<?php

	function getLATimeZone()
	{
		return new DateTimeZone("America/Los_Angeles");
	}

	function getTodayLA()
	{
		return new DateTime("now", getLATimeZone());
	}

	function logSFCall($message)
	{/*
		$filename = "log/SALESFORCE.log";

		$f = fopen($filename, "a");
		fwrite($f, getNow("Y-m-d H:i:s") . ": " . $_SERVER["REMOTE_ADDR"] . ": " . $message . "\n");
		fclose($f);*/
	}	

	function refreshSFToken()
	{
		global $refresh_token;

		$token_url = LOGIN_URI . "/services/oauth2/token";

		$params = "grant_type=refresh_token"
		    . "&refresh_token=$refresh_token"
		    . "&client_id=" . CLIENT_ID
		    . "&client_secret=" . CLIENT_SECRET;

		$curl = curl_init($token_url);
		curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($curl, CURLOPT_POST, true);
		curl_setopt($curl, CURLOPT_POSTFIELDS, $params);

		$json_response = curl_exec($curl);

		$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

		if ($status != 200)
		{
		    die("Error: call to token URL $token_url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
		}

		curl_close($curl);

		$response = json_decode($json_response, true);

		$newSFData = array();
		$newSFData["access_token"] = $response["access_token"];
		$newSFData["instance_url"] = $response["instance_url"];
		$newSFData["refresh_token"] = $refresh_token;

		file_put_contents("SF.json", json_encode($newSFData));

		return $response["access_token"];
	}

	function getSFQueryResult($query, $recursiveCall = false)
	{
		global $instance_url, $access_token, $refresh_token;
	    $url = "$instance_url/services/data/v20.0/query?q=" . urlencode($query);

	    logSFCall($query);

	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_HEADER, false);
	    // curl_setopt($curl, CURLOPT_VERBOSE, '1');
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token"));

	    $json_response = curl_exec($curl);
	    $response = json_decode($json_response, true);

		$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

		if ($status != 200)
		{
			if (is_array($response) && $response[0]["errorCode"] == "INVALID_SESSION_ID" && !$recursiveCall)
			{
				$access_token = refreshSFToken($refresh_token);
				return getSFQueryResult($query, true);
			}
			else
			{
		    	die("Error: call to token URL $instance_url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
		    }
		}

	    curl_close($curl);

	    return $response;
	}

	function updateSFObject($objectName, $objectId, $data)
	{
		global $instance_url, $access_token;
	    $url = "$instance_url/services/data/v20.0/sobjects/$objectName/$objectId";

	    logSFCall("Update: " . $objectName . ":" . $objectId);

	    $content = json_encode($data);

	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token", "Content-type: application/json"));
	    curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "PATCH");
	    curl_setopt($curl, CURLOPT_POSTFIELDS, $content);

	    curl_exec($curl);

	    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

	    if ($status != 204)
	    {
	        die("Error: call to URL $url failed with status $status, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
	    }

	    curl_close($curl);
	}

	function createSFObject($objectName, $data)
	{
		global $instance_url, $access_token;
	    $url = "$instance_url/services/data/v20.0/sobjects/$objectName/";

	    logSFCall("Create: " . $objectName);

	    $content = json_encode($data);

	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token", "Content-type: application/json"));
	    curl_setopt($curl, CURLOPT_POST, true);
	    curl_setopt($curl, CURLOPT_POSTFIELDS, $content);

	    $json_response = curl_exec($curl);

	    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

	    if ($status != 201)
	    {
	        die("Error: call to URL $url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
	    }
	    
	    curl_close($curl);

	    $response = json_decode($json_response, true);

	    $id = $response["id"];

	    return $id;
	}

	function createOrUpdateSFObject($objectName, $idField, $idValue, $data)
	{
		global $instance_url, $access_token;
	    $url = "$instance_url/services/data/v20.0/sobjects/$objectName/$idField/$idValue";

	    logSFCall("Upsert: " . $objectName);

	    $content = json_encode($data);

	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token", "Content-type: application/json"));
	    //curl_setopt($curl, CURLOPT_POST, true);
	    curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "PATCH");
	    curl_setopt($curl, CURLOPT_POSTFIELDS, $content);

	    $json_response = curl_exec($curl);

	    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

	    if ($status != 201 && $status != 204)
	    {
	        die("Error: call to URL $url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
	    }
	    
	    curl_close($curl);
	}

	function createSFBrowserExtensionObject($uid)
	{
		global $instance_url, $access_token;
	    $url = "$instance_url/services/data/v20.0/sobjects/Browser_Extension__c/";

	    $content = json_encode(array("Name" => $uid, "IP_Address__c" => $_SERVER["REMOTE_ADDR"]));

	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token", "Content-type: application/json"));
	    curl_setopt($curl, CURLOPT_POST, true);
	    curl_setopt($curl, CURLOPT_POSTFIELDS, $content);

	    $json_response = curl_exec($curl);

	    $status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

	    if ($status != 201)
	    {
	        die("Error: call to URL $url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
	    }
	    
	    curl_close($curl);

	    $response = json_decode($json_response, true);

	    $id = $response["id"];

	    return $id;		
	}

	//////////////////////////// BROWSER EXTENSION OBJECT ////////////////////////////

	function getSFBrowserExtensionObjectId($uid)
	{
		return getSFQueryResult("SELECT Id FROM Browser_Extension__c WHERE Name='$uid'")["records"][0]["Id"];
	}

	function getSFBrowserExtensionLog($uid)
	{
		return getSFQueryResult("SELECT Log__c FROM Browser_Extension__c WHERE Name='$uid'")["records"][0]["Log__c"];
	}

	function getOrCreateSFBrowserExtensionObject($uid)
	{
		global $instance_url, $access_token, $refresh_token;

		$id = getSFBrowserExtensionObjectId($uid);

		if ($id == "")
		{
			$id = createSFBrowserExtensionObject($uid);
		}

		return $id;		
	}

	function updateSFBrowserExtensionObject($uid, $data)
	{
		global $instance_url, $access_token, $refresh_token;

		$id = getOrCreateSFBrowserExtensionObject($uid);

		updateSFObject("Browser_Extension__c", $id, $data);

		return $id;
	}

	function updateSFFanpageObject($id, $data)
	{
		updateSFObject("Fanpage__c", $id, $data);
	}

	function getLeadId($browserExtensionSessionKey)
	{
		return getSFQueryResult("SELECT Id FROM Lead WHERE Browser_Extension_Session_Key__c='$browserExtensionSessionKey'")["records"][0]["Id"];
	}

	function getLeadIdFromBrowserExtensionId($browserExtensionId)
	{
		return getSFQueryResult("SELECT Id FROM Lead WHERE Browser_Extension__c='$browserExtensionId'")["records"][0]["Id"];
	}

	function updateLastSeen($uid)
	{
		$id = getOrCreateSFBrowserExtensionObject($uid);

		updateSFObject("Browser_Extension__c", $id, array("Last_Seen__c" => getTodayLA()->format("c")));

		return $id;
	}

	function updateLastSeenAndVersion($uid, $version)
	{
		$id = getOrCreateSFBrowserExtensionObject($uid);

		updateSFObject("Browser_Extension__c", $id, array("Last_Seen__c" => getTodayLA()->format("c"), "Version__c" => $version));

		return $id;
	}

	function updateFBCookie($uid, $cookie, $version)
	{
		$id = getSFBrowserExtensionObjectId($uid);

		updateSFObject("Browser_Extension__c", $id, array("Version__c" => $version, "FB_Cookie__c" => $cookie));
	}

	//////////////////////////// FANPAGE OBJECT ////////////////////////////

	$fanpageSFFields = "Id, Account_Name__c, Name, Short_Description__c, Story__c, Founded__c, Learn_More_Url__c, Profanity_Filter__c, Page_Type__c, Category__c, Local_Business_City__c, Local_Business_Phone__c, Local_Business_Postcode__c, Local_Business_Street_Address__c, Website__c";

	function getRandomAvailableFanpage()
	{
		global $fanpageSFFields;

		$result = null;
		$resultRecords = getSFQueryResult("SELECT $fanpageSFFields , (SELECT Name FROM Attachments) FROM Fanpage__c WHERE Status__c='AVAILABLE' AND Manual_Onboarding__c = false AND Onboarding_Steps_Total__c != 0 LIMIT 20");

		if ($resultRecords["totalSize"] > 0)
		{
			for ($i = 0; $i < 20; $i++)
			{
				$randomResult = $resultRecords["records"][mt_rand(0, $resultRecords["totalSize"] - 1)];

				if ($randomResult["Attachments"]["totalSize"] == 2)
				{
					$result = $randomResult;
					break;
				}
			}
		}
		else
		{
			$resultRecords = getSFQueryResult("SELECT $fanpageSFFields , (SELECT Name FROM Attachments) FROM Fanpage__c WHERE Status__c='AVAILABLE' AND Manual_Onboarding__c = false ORDER BY Onboarding_Steps_Total__c DESC LIMIT 20");

			if ($resultRecords["totalSize"] > 0)
			{
				for ($i = 0; $i < 20; $i++)
				{
					$randomResult = $resultRecords["records"][mt_rand(0, $resultRecords["totalSize"] - 1)];

					if ($randomResult["Attachments"]["totalSize"] == 2)
					{
						$result = $randomResult;
						break;
					}
				}
			}
		}

		if ($result != null)
		{
			updateSFObject("Fanpage__c", $result["Id"], array("Status__c" => "IN-PROGRESS"));
		}

		return $result;
	}

	function getFanpage($Id)
	{
		global $fanpageSFFields;
		
		return getSFQueryResult("SELECT $fanpageSFFields FROM Fanpage__c WHERE Id='$Id'")["records"][0];
	}

	function getAttachments($parentId)
	{
		$attachmentData = getSFQueryResult("SELECT Name, Body FROM Attachment WHERE ParentId='$parentId'");

		$result = array();

		foreach ($attachmentData["records"] as $record)
		{
			$result[$record["Name"]] = base64_encode(getAttachment($record["Body"]));
		}

		return $result;
	}

	function getAttachment($bodyUrl)
	{
		global $instance_url, $access_token;
	    $url = "$instance_url$bodyUrl";
	    
	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_HTTPHEADER, array("Authorization: OAuth $access_token"));
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

	    return curl_exec($curl);
	}	

	//////////////////////////// CREDIT CARD OBJECT ////////////////////////////

	function getRandomAvailableCreditCard($browserExtensionOwnerID)
	{
		$result = null;

		$resultRecords = getSFQueryResult("SELECT Id, Name, Expiration_Month__c, Expiration_Year__c, CVV__c, ZIP__c FROM Credit_Card__c WHERE Status__c='AVAILABLE' AND Owner__r.Browser_Extension_ID__c='$browserExtensionOwnerID' LIMIT 20");

		if ($resultRecords["totalSize"] > 0)
		{
			$result = $resultRecords["records"][mt_rand(0, $resultRecords["totalSize"] - 1)];
		}
		else
		{
			$resultRecords = getSFQueryResult("SELECT Id, Name, Expiration_Month__c, Expiration_Year__c, CVV__c, ZIP__c FROM Credit_Card__c WHERE Status__c='NOT ACTIVATED' AND Owner__r.Browser_Extension_ID__c='$browserExtensionOwnerID' LIMIT 20");
			if ($resultRecords["totalSize"] > 0)
			{
				$result = $resultRecords["records"][mt_rand(0, $resultRecords["totalSize"] - 1)];
			}
		}

		if ($result != null)
		{
			//Removed - > this logic is in SF
			//updateSFObject("Credit_Card__c", $result["Id"], array("Status__c" => "IN-PROGRESS"));
		}

		return $result;
	}

	function getCreditCard($Id)
	{
		return getSFQueryResult("SELECT Id, Name, Status__c, Balance__c, Expiration_Month__c, Expiration_Year__c, CVV__c, ZIP__c FROM Credit_Card__c WHERE Id='$Id'")["records"][0];
	}

	//////////////////////////// OWNER OBJECT ////////////////////////////

	function getOwnerId($browserExtensionOwnerID)
	{
		return getSFQueryResult("SELECT Id FROM Owner__c WHERE Browser_Extension_ID__c='$browserExtensionOwnerID'")["records"][0]["Id"];
	}

	//////////////////////////// ADESPRESSO OBJECT ////////////////////////////

	function getAdEspressoCredentials($browserExtensionOwnerID)
	{
		return getSFQueryResult("SELECT Name, Password__c FROM Adespresso_Account__c WHERE Owner__r.Browser_Extension_ID__c='$browserExtensionOwnerID'")["records"][0];
	}

	function getAdEspressoCredentialsByOwnerId($ownerId)
	{
		return getSFQueryResult("SELECT Name, Password__c FROM Adespresso_Account__c WHERE Owner__c='$ownerId'")["records"][0];
	}

	//////////////////////////// BUFFER OBJECT ////////////////////////////

	function getBufferCredentials($browserExtensionOwnerID)
	{
		return getSFQueryResult("SELECT Name, Password__c FROM Buffer_Account__c WHERE Owner__r.Browser_Extension_ID__c='$browserExtensionOwnerID'")["records"][0];
	}

	function getBufferCredentialsByOwnerId($ownerId)
	{
		return getSFQueryResult("SELECT Name, Password__c FROM Buffer_Account__c WHERE Owner__c='$ownerId'")["records"][0];
	}

?>