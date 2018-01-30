<html>

<head>
	<link rel="icon" href="http://adsrental.com/rasbpi_icon.ico" />
	<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
	<title>Pi Dashboard</title>
	
	<script type="text/javascript">
		setTimeout(function() { window.location.reload(); }, 60 * 1000);
		
		window.addEventListener("load", function() {
			document.querySelector("#lastUpdatedTag").textContent = (new Date()).toString();
		});
	</script>
</head>

<body>

	<table class="table table-bordered">
	
	<tr>
		<th>#</th>
		<th>Account</th>
		<th>Lead</th>
		<th>Raspberry Pi</th>
		<th>Online</th>
		<th>First Tested</th>
		<th>Tunnel Last Tested</th>
		<th>RDP</th>
	</tr>
	
<?php

	//ini_set('display_errors', 1);

	require_once("include/AWSSDK/aws-autoloader.php");
	require_once("include/ec2helpers.inc");
	
	require_once("include/mysql.inc");
	
	$rows = mysqlSelectTestingRaspberryPis();
	
	$rowNumber = 1;
	
	foreach ($rows as $row)
	{/*
		if (!$row["tunnel_online"] && empty($row["ec2_hostname"]))
		{
			mysqlUpdateRaspberryPiEC2Hostname($row["rpid"]);
		}*/
		
		echo "<tr>\n";
		echo "<td>" . sprintf("%02d", $rowNumber) . "</td>";
		echo "<td title='" . print_r($row, true) ."'>" . $row["account_name"] . "</td>";
		echo "<td><a href='https://na40.salesforce.com/$row[leadid]' target='_blank'>" . $row["first_name"] . " " . $row["last_name"] . "</td>";
		echo "<td><a href='https://adsrental.com/log/$row[rpid]' target='_blank' title='IP ADDRESS: $row[ipaddress]' alt='IP ADDRESS: $row[ipaddress]'>$row[rpid]</a></td>";
		echo "<td>" . ($row["online"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span>" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span>") . "</td>";
		echo "<td>" . $row["first_tested"] . "</td>";
		echo "<td>" . $row["tunnel_last_tested"] . "</td>";
		echo "<td><a href='https://adsrental.com/app/rdp/$row[rpid]/' target='_blank'>$row[rpid]</a></td>";
		echo "</tr>\n";
		
		$rowNumber++;
	}
?>

	</table>
	
	<small>Last updated <span id="lastUpdatedTag"></span></small>
</body>

</html>