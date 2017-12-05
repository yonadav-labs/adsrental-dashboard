<?php

	function getIPInfo($ipAddress)
	{
		return getJSON("http://ip-api.com/json/" . $ipAddress);
	}

	function getASN($ipAddress)
	{
		$json = getIPInfo($ipAddress);
		$arr = isset($json["as"] ) ? explode(" ", $json["as"] || "") : "";

		return $arr ? $arr[0] : "";
	}

	function isFacebookASN($ipAddress)
	{
		return getASN($ipAddress) == "AS32934";
	}

?>