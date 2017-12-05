<?php

	function get($url)
	{
	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_HEADER, false);
	    // curl_setopt($curl, CURLOPT_VERBOSE, '1');
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

	    return curl_exec($curl);	
	}
	
	function getBasicAuthentication($url, $username, $password)
	{
	    $curl = curl_init($url);
	    curl_setopt($curl, CURLOPT_HEADER, false);
	    // curl_setopt($curl, CURLOPT_VERBOSE, '1');
	    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($curl, CURLOPT_USERPWD, $username . ":" . $password);
		curl_setopt($curl, CURLOPT_HTTPHEADER, array("Accept: application/json"));

	    return curl_exec($curl);	
	}
	
	function getBasicAuthenticationJSON($url, $username, $password)
	{
		return json_decode(getBasicAuthentication($url, $username, $password), true);
	}

	function getJSON($url)
	{
	    return json_decode(get($url), true);
	}

?>