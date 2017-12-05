<?php
	ini_set('display_errors', 1);

	require_once("include/config.php");

	$token_url = LOGIN_URI . "/services/oauth2/token";

	$code = $_GET["code"];

	if (!isset($code) || $code == "")
	{
	    die("Error - code parameter missing from request!");
	}

	$params = "code=" . $code
	    . "&grant_type=authorization_code"
	    . "&client_id=" . CLIENT_ID
	    . "&client_secret=" . CLIENT_SECRET
	    . "&redirect_uri=" . urlencode(REDIRECT_URI);

	$curl = curl_init($token_url);
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_POST, true);
	curl_setopt($curl, CURLOPT_POSTFIELDS, $params);

	$json_response = curl_exec($curl);

	$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

	if ( $status != 200 )
	{
	    die("Error: call to token URL $token_url failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
	}

	curl_close($curl);

	$response = json_decode($json_response, true);

	$newSFData = array();
	$newSFData["access_token"] = $response["access_token"];
	$newSFData["instance_url"] = $response["instance_url"];
	$newSFData["refresh_token"] = $response["refresh_token"];

	file_put_contents("SF.json", json_encode($newSFData));

?>