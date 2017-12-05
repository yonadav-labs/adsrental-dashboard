<?php

	ini_set('display_errors', 1);

	$session = curl_init();

	$customerio_url = "https://track.customer.io/api/v1/customers/";
	$site_id = "82d3c319eddf928c6d3b";
	$api_key = "a3f8c67888863a8f1e1c";

	$customer_id = $_GET["id"];

	$attributes = array();

	foreach ($_GET as $key => $value)
	{
		if ($key != "name")
		{
			$attributes[$key] = $value;
		}
	}

	$data = array("name" => $_GET["name"], "data" => $attributes);

	// Creates or updates a user with the ID 1337, email test@example.com and a created_at timestamp
	curl_setopt($session, CURLOPT_URL, $customerio_url . $customer_id . "/events");
	curl_setopt($session, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
	curl_setopt($session, CURLOPT_HEADER, false);
	curl_setopt($session, CURLOPT_RETURNTRANSFER, true);
	// curl_setopt($session, CURLOPT_VERBOSE, '1');
	curl_setopt($session, CURLOPT_CUSTOMREQUEST, "POST");
	curl_setopt($session, CURLOPT_POSTFIELDS,http_build_query($data));
	curl_setopt($session, CURLOPT_USERPWD, $site_id . ":" . $api_key);

	curl_setopt($session,CURLOPT_SSL_VERIFYPEER,false);

	$response = curl_exec($session);
	// echo $response;
	curl_close($session);

?>