<?php
	require_once("include/config.php");

	$auth_url = LOGIN_URI
	        . "/services/oauth2/authorize?response_type=code&client_id="
	        . CLIENT_ID . "&redirect_uri=" . urlencode(REDIRECT_URI) . "&scope=full refresh_token";

	header("Location: " . $auth_url);
?>