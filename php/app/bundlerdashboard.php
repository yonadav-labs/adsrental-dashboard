<?php
	function array_to_csv_download($array, $filename = "export.csv", $delimiter=";") {
		header('Content-Type: application/csv');
		header('Content-Disposition: attachment; filename="'.$filename.'";');

		$f = fopen('php://output', 'w');

		foreach ($array as $line) {
			fputcsv($f, $line, $delimiter);
		}
	}

	function draw_table($rows) {
		$output = array();
		$output[] = "<table class=\"table table-bordered\" id=\"results\">";
		
		$output[] = "<tr>" .
			"<th>#</th>" .
			"<th>Account</th>" .
			"<th>Lead</th>" .
			"<th>Phone</th>" .
			"<th>Address</th>" .
			"<th>Raspberry Pi</th>" .
			"<th>Google</th>" .
			"<th>Facebook</th>" .
			"<th>Online</th>" .
			"<th>First Seen</th>" .
			"<th>Last Seen</th>" .
			"<th>Tunnel Last Tested</th>" .
			"<th>Bundler Paid</th>" .
			"<th>Wrong Password</th>" .
			"<th>Pi Delivered</th>" .
		"</tr>";

		$rowNumber = 1;
	
		foreach ($rows as $row)
		{
			$output[] = "<tr>\n";
			$output[] = "<td>" . sprintf("%02d", $rowNumber) . "</td>";
			$output[] = "<td title='" . print_r($row, true) ."'>" . $row["account_name"] . "</td>";
			$output[] = "<td><a href='https://na40.salesforce.com/$row[leadid]' target='_blank'>" . $row["first_name"] . " " . $row["last_name"] . "</a><br />" . $row["email"] . "</td>";
			$output[] = "<td>$row[phone]</td>";
			$output[] = "<td>";
			$output[] = "    $row[address]";
			$output[] = "    $row[usps_tracking_code]";
			$output[] = "</td>";
			$output[] = "<td>";
			$output[] = "    $row[rpid] ($row[ipaddress])";
			$output[] = "    <br /><a href='https://adsrental.com/log/$row[rpid]' target='_blank'>Logs</a>";
			$output[] = "    <a href='https://adsrental.com/rdp.php?i=$row[rpid]&h=$row[rpid]' target='_blank'>RDP</a>";
			$output[] = "</td>";
			$output[] = "<td>" . ($row["google_account"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span>" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span>") . "</td>";
			$output[] = "<td>" . ($row["facebook_account"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span>" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span>") . "</td>";
			$output[] = "<td style=\"white-space: nowrap;\">";
			$output[] = "    " . ($row["online"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span> Online" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span> Offline");
			$output[] = "    <br />" . ($row["tunnel_online"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span> Tunnel" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span> Tunnel");
			$output[] = "    <br /><a href=\"http://$row[ec2_hostname]:13608/start-tunnel\">Restart tunnel</a>";
			$output[] = "</td>";
			$output[] = "<td title=\"" . $row["first_seen"]. "\">" . time_elapsed_string($row["first_seen"]) . "</td>";
			$output[] = "<td title=\"" . $row["last_seen"]. "\">" . time_elapsed_string($row["last_seen"]) . "</td>";
			$output[] = "<td title=\"" . $row["tunnel_last_tested"]. "\">" . time_elapsed_string($row["tunnel_last_tested"]) . "</td>";
			$output[] = "<td>" . ($row["bundler_paid"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span>" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span>") . "</td>";
			$output[] = "<td>" . ($row["wrong_password"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: red;\"></span>" : "No") . "</td>";
			$output[] = "<td>" . ($row["pi_delivered"] ? "<span class=\"glyphicon glyphicon-ok\" style=\"color: lightgreen;\"></span>" : "<span class=\"glyphicon glyphicon-remove\" style=\"color: red;\"></span>") . "</td>";			
			$output[] = "</tr>\n";
	
			$rowNumber++;
		}
		
		$output[] = "</table>";
		return join("", $output);
	}

	function time_elapsed_string($datetime, $full = false) {
		$now = new DateTime;
		if (!$datetime){
			return "never";
		}
		$ago = new DateTime($datetime);

		// FIXME: SF adds 7 hours :(
		$ago->add(new DateInterval("PT7H"));
		if ($ago > $now){
			return 'Just now';
		}

		$diff = $now->diff($ago);
	
		$diff->w = floor($diff->d / 7);
		$diff->d -= $diff->w * 7;
	
		$string = array(
			'y' => 'year',
			'm' => 'month',
			'w' => 'week',
			'd' => 'day',
			'h' => 'hour',
			'i' => 'minute',
			's' => 'second',
		);
		foreach ($string as $k => &$v) {
			if ($diff->$k) {
				$v = $diff->$k . ' ' . $v . ($diff->$k > 1 ? 's' : '');
			} else {
				unset($string[$k]);
			}
		}
	
		if (!$full) $string = array_slice($string, 0, 1);
		return $string ? implode(', ', $string) . ' ago' : ' just now';
	}
?>

<?php

    if (!array_key_exists("utm_source", $_GET))
    {
        exit;
    }
	
	require_once("include/AWSSDK/aws-autoloader.php");
	require_once("include/ec2helpers.inc");

	require_once("include/mysql.inc");

	$rows = mysqlSelectAllRaspberryPis(array("utm_source" => $_GET["utm_source"]));
	$csv_link = "http://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]&csv=true";

	$filtered = array();
	foreach ($rows as $row) {
		if (isset($_GET["offline_only"]) && $_GET["offline_only"] && $row['online']) {
			continue;
		}
		if (isset($_GET["online_only"]) && $_GET["online_only"] && !$row['online']) {
			continue;
		}
		if (isset($_GET["tunnel_offline_only"]) && $_GET["tunnel_offline_only"] && $row['tunnel_online']) {
			continue;
		}
		$filtered[] = $row;
	}
	$rows = $filtered;

	if (array_key_exists("csv", $_GET))
	{
		$csv_rows = Array();
		foreach ($rows as $row) {
			$csv_rows[] = Array(
				"leadid" => $row["leadid"],
				"account_name" => $row["account_name"],
				"first_name" => $row["first_name"],
				"last_name" => $row["last_name"],
				"email" => $row["email"],
				"phone" => $row["phone"],
				"address" => $row["address"],
				"ipaddress" => $row["ipaddress"],
				"usps_tracking_code" => $row["usps_tracking_code"],
				"google_account" => $row["google_account"],
				"facebook_account" => $row["facebook_account"],
				"online" => $row["online"],
				"tunnel_online" => $row["tunnel_online"],
				"first_seen" => $row["first_seen"],
				"last_seen" => $row["last_seen"],
				"tunnel_last_tested" => $row["tunnel_last_tested"],
				"wrong_password" => $row["wrong_password"],
				"bundler_paid" => $row["bundler_paid"],
				"rpid" => $row["rpid"],
			);
		}
		array_to_csv_download($csv_rows);
		exit;
	}

	if (array_key_exists("table", $_GET)) {
		echo draw_table($rows);
		exit;
	}

?>

<html>

<head>
	<link rel="icon" href="http://adsrental.com/rasbpi_icon.ico" />
	<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
	<script
		src="https://code.jquery.com/jquery-3.2.1.min.js"
		integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
		crossorigin="anonymous"></script>
	<title>Pi Dashboard</title>
</head>

<body>
	<div class="container">
		<h2>Pi Dashboard</h2>
		<form action="">
		<input type="hidden" name="utm_source" value="<?php echo $_GET['utm_source'] ?>" />
			<div class="form-check">
				<label class="form-check-label">
				<input type="checkbox" name="online_only" value="true" <?php echo isset($_GET['online_only'])?"checked":"" ?> />
				Online only
				</label>
			</div>
			<input type="hidden" name="utm_source" value="<?php echo $_GET['utm_source'] ?>" />
			<div class="form-check">
				<label class="form-check-label">
				<input type="checkbox" name="offline_only" value="true" <?php echo isset($_GET['offline_only'])?"checked":"" ?> />
				Offline only
				</label>
			</div>
			<div class="form-check">
				<label class="form-check-label">
				<input type="checkbox" name="tunnel_offline" value="true" <?php echo isset($_GET['tunnel_offline_only'])?"checked":"" ?> />
				Tunnel offline only
				</label>
			</div>
			<button class="btn btn-primary">Submit</button>
			<button class="btn btn-secondary" name="csv" value="true">Download CSV</button>
		</form>
	</div>

	<div id="hidden" style="display:none;"></div>
	<?php echo draw_table($rows); ?>

	<small>Last updated <span id="lastUpdatedTag"></span></small>


	<script type="text/javascript">
		$(function(){
			$("#lastUpdatedTag").text((new Date()).toString());
			setInterval(function() {
				var url = document.location.href + '&table=true';
				$.get(url, function(data){
					var oldResults = $('#results');
					$('#hidden').empty();
					$('#hidden').append($(data));
					var newResults = $('#hidden').find('#results');
					oldResults.replaceWith(newResults);
					$("#lastUpdatedTag").text((new Date()).toString());
				})
	
			}, 60 * 1000);
		})
	</script>

</body>

</html>