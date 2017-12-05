<?php

	if (!array_key_exists("rpid", $_GET))
	{
		exit;
	}

    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename=pi.conf');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');

	echo $_GET["rpid"];

    exit;
	
?>