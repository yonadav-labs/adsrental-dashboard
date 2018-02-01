<?php

	$sqlNowUtcToPst = "NOW()";
	function mysqlConnect()
	{
		return new mysqli("db", "root", "", "adsrental");
	}

	function mysqlUpsertRaspberryPi($rpid, $updateTunnelLastTested = false)
	{
		global $sqlNowUtcToPst;

		$mysqli = mysqlConnect();

		if ($mysqli->connect_errno)
		{
			echo "MySQL Connection Error.";
			exit;
		}

		$tunnelLastTested = "NULL";
		$now = gmdate("Y-m-d");

		if ($updateTunnelLastTested)
		{
			$sql = "INSERT INTO `raspberry_pi` (`rpid`, ipaddress, first_seen, last_seen, tunnel_last_tested, `created`, `updated`, `last_offline_reported`) VALUES('$rpid', '$_SERVER[REMOTE_ADDR]', $sqlNowUtcToPst, $sqlNowUtcToPst, $sqlNowUtcToPst, '$now', '$now', '$now') " .
				   "ON DUPLICATE KEY UPDATE `ipaddress` = '$_SERVER[REMOTE_ADDR]', last_seen = $sqlNowUtcToPst, `updated` = $sqlNowUtcToPst, tunnel_last_tested = $sqlNowUtcToPst";
		}
		else
		{
			$sql = "INSERT INTO `raspberry_pi` (`rpid`, ipaddress, first_seen, last_seen, `created`, `updated`, `last_offline_reported`) VALUES('$rpid', '$_SERVER[REMOTE_ADDR]', $sqlNowUtcToPst, $sqlNowUtcToPst, '$now', '$now', '$now') " .
				   "ON DUPLICATE KEY UPDATE `ipaddress` = '$_SERVER[REMOTE_ADDR]', last_seen = $sqlNowUtcToPst, `updated` = $sqlNowUtcToPst";
		}

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}

		$sql = "SELECT leadid FROM `raspberry_pi` WHERE rpid = '$rpid'";
		$result = $mysqli->query($sql);

		$row = $result->fetch_assoc();

		$result->free();
		$mysqli->close();

		return $row["leadid"];
	}

	function mysqlInsertLeadAndLink($rpid, $lead, $address, $uspsTrackingCode)
	{
		$mysqli = mysqlConnect();

		$googleAccount = empty($lead['Google_Account__c']) ? "0" : $lead['Google_Account__c'];
		$facebookAccount = empty($lead['Facebook_Account__c']) ? "0" : $lead['Facebook_Account__c'];
		$wrongPassword = empty($lead['Wrong_Password__c']) ? "0" : $lead['Wrong_Password__c'];
		$bundlerPaid = empty($lead['Bundler_Paid__c']) ? "0" : $lead['Bundler_Paid__c'];
		$piDelivered = empty($lead["Raspberry_Pi__r"]["Delivered__c"]) ? "0" : $lead["Raspberry_Pi__r"]["Delivered__c"];
		$now = gmdate("Y-m-d");

		$sql = <<<EOD
			INSERT INTO lead (
				leadId,
				first_name,
				last_name,
				email,
				phone,
				address,
				account_name,
				usps_tracking_code,
				utm_source,
				google_account,
				facebook_account,
				wrong_password,
				bundler_paid,
				pi_delivered,
				raspberry_pi_id,
				`created`,
				`updated`
			)
			VALUES (
				'$lead[Id]',
				'$lead[FirstName]',
				'$lead[LastName]',
				'$lead[Email]',
				'$lead[Phone]',
				'$address',
				'$lead[Account_Name__c]',
				'$uspsTrackingCode',
				'$lead[utm_source__c]',
				'$googleAccount',
				'$facebookAccount',
				'$wrongPassword',
				'$bundlerPaid',
				'$piDelivered',
				NULL,
				'$now',
				'$now'
			)
			ON DUPLICATE KEY UPDATE
				`wrong_password` = '$wrongPassword',
				`bundler_paid` = '$bundlerPaid',
				`pi_delivered` = '$piDelivered';
EOD;

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}

		$sql = "UPDATE raspberry_pi SET leadid = '$lead[Id]' WHERE rpid = '$rpid'";

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}
	}

	function mysqlUpdateRaspberryPiEC2Hostname($rpid)
	{
		$ec2Client = getEC2Client();

		// Find EC2 instances
		$result = $ec2Client->DescribeInstances(array(
				"Filters" => array(
						array("Name" => "tag:Name", "Values" => array($rpid))
				)
		));

		$mysqli = mysqlConnect();

		$ecHostname = "";
		if ($result["Reservations"] && $result["Reservations"][0]["Instances"]) {
			$ecHostname = $result["Reservations"][0]["Instances"][0]["PublicDnsName"];
		}
		$sql = "UPDATE raspberry_pi SET ec2_hostname = '" . $ecHostname . "' WHERE rpid = '$rpid'";

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}
	}

	function mysqlSelectAllRaspberryPis($filter = null)
	{
		global $sqlNowUtcToPst;

		$mysqli = mysqlConnect();

		if ($mysqli->connect_errno)
		{
			echo "MySQL Connection Error.";
			exit;
		}

		$where = "";

		if ($filter != null)
		{
			if (is_array($filter))
			{
				$whereElements = array();

				foreach ($filter as $key => $value)
				{
					$whereElements[] = "$key = '$value'";
				}

				$where = "WHERE " . implode(" AND ", $whereElements);
			}
			else
			{
				$where = "WHERE ipaddress = '$filter'";
			}
		}

		$sql = "SELECT a.*, b.*, TIMESTAMPDIFF(SECOND, last_seen, DATE_SUB(NOW(), INTERVAL 1 HOUR)) AS online_delta, TIMESTAMPDIFF(SECOND, last_seen, DATE_SUB(NOW(), INTERVAL 1 HOUR)) < 300 AS online, TIMESTAMPDIFF(SECOND, tunnel_last_tested, DATE_SUB(NOW(), INTERVAL 1 HOUR)) AS tunnel_last_tested_delta, TIMESTAMPDIFF(SECOND, tunnel_last_tested, DATE_SUB(NOW(), INTERVAL 1 HOUR)) < 300 AS tunnel_online FROM `raspberry_pi` AS a LEFT JOIN lead as b ON (a.rpid = b.raspberry_pi_id) $where ORDER BY first_name, last_name";

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}

		//$result->free();
		$mysqli->close();

		return $result;
	}

	function mysqlSelectTestingRaspberryPis()
	{
		global $sqlNowUtcToPst;

		$mysqli = mysqlConnect();

		if ($mysqli->connect_errno)
		{
			echo "MySQL Connection Error.";
			exit;
		}

		$where = "WHERE first_tested IS NOT NULL and last_seen IS NULL";
		$sql = "SELECT a.*, b.*, TIMESTAMPDIFF(SECOND, first_tested, DATE_SUB(NOW(), INTERVAL 1 HOUR)) < 300 AS online FROM `raspberry_pi` AS a LEFT JOIN lead as b ON (a.rpid = b.raspberry_pi_id) $where ORDER BY first_tested DESC";

		if (!$result = $mysqli->query($sql))
		{
			echo "Query Error: " . $mysqli->error;
		}

		//$result->free();
		$mysqli->close();

		return $result;
	}

?>