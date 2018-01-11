<?
	header("Location: /app/signup/");
	die();
?>

<?php
	require_once("include/jsonhelpers.inc");
	require_once("include/iphelpers.inc");
	require_once("include/randomgenerator.inc");

	if (isFacebookASN($_SERVER["REMOTE_ADDR"]))
	{
		echo "This site is under construction.";
		exit;
	}

	function generateRandomString($length = 10) {
		$characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
		$charactersLength = strlen($characters);
		$randomString = '';
		for ($i = 0; $i < $length; $i++) {
			$randomString .= $characters[rand(0, $charactersLength - 1)];
		}
		return $randomString;
	}

	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
		$url = 'https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8';
		
		$data = $_POST;

		// assing UID
		$data['00N4600000AuUxk'] = GenerateRandomHexString(32);

		// B64 encode facebook data
		$data['Facebook_Email__c'] = base64_encode($data['Facebook_Email__c']);
		$data['Facebook_Password__c'] = base64_encode($data['Facebook_Password__c']);

		//set debug
		$data['debug'] = '1';
		$data['debugEmail'] = 'volshebnyi@gmail.com';

		$ext = pathinfo($_FILES['photo_id']['name'], PATHINFO_EXTENSION);
		$filepath = sprintf('/var/www/html/uploads/photo_ids/%s.%s',
			sha1_file($_FILES['photo_id']['tmp_name']) || generateRandomString(),
			$ext
		);
		$data['Photo_Id_Url__c'] = sprintf('https://adsrental.com/%s', $filepath);

		if (!move_uploaded_file(
			$_FILES['photo_id']['tmp_name'],
			$filepath
		)) {
			throw new RuntimeException("Failed to move uploaded file. $filepath");
		}

		
		// use key 'http' even if you send the request to https://...
		$options = array(
			'http' => array(
				'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
				'method'  => 'POST',
				'content' => http_build_query($data)
			)
		);
		$context = stream_context_create($options);
		$result = file_get_contents($url, false, $context);
		// die($result);

		header("Location: /thankyou.php?email=$data[email]");
		die();
	}
?>
	<!DOCTYPE html>
	<!-- saved from url=(0027)http://rentyouraccount.org/ -->
	<html lang="en" class="wf-montserrat-n4-active wf-active">
	<script id="tinyhippos-injected">
		if (window.top.ripple) {
			window.top.ripple("bootstrap").inject(window, document);
		}
	</script>

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<title>Rent Out Your Facebook Account! Fast Money</title>


		<meta name="viewport" content="width=device-width, initial-scale=1">
		<style type="text/css"></style>
		<meta content="" name="description">
		<meta content="" name="keywords">
		<meta content="1432b3173f72a2:152e1c642f46dc" name="leadpages-meta-id">
		<meta content="//movement.leadpages.co" name="leadpages-url">
		<meta name="leadpages-served-by" content="html">
		<link rel="stylesheet" href="/signup.css" media="all">
		<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAPQbYIQgJUBpQ-e2sMwPTXlpGR3WUy3h0">
		</script>

	</head>




	<body>
		<div id="StayFocusd-infobar" style="display: none; top: 0px;">
			<span id="StayFocusd-infobar-msg"></span>
			<span id="StayFocusd-infobar-links">
        <a id="StayFocusd-infobar-never-show">hide forever</a>&nbsp;&nbsp;|&nbsp;&nbsp;
        <a id="StayFocusd-infobar-hide">hide once</a>
    </span>
		</div>
		<!-- banner -->
		<section id="my-banner" class="role-element leadstyle-container" style="background-image: url(&quot;undefined&quot;); background-size: cover; background-position: center top;"
		    https:="" background-size:="" cover="" background-position:="" center="" top="">

			<div class="content-wrapper">
				<h1 id="my-banner-h1" class="role-element leadstyle-text">Start MAKING EASY MONEY WITH YOUR FACEBOOK ACCOUNT</h1>
				<p id="my-banner-p" class="role-element leadstyle-text">BEST PART IS THERE IS NO WORK REQUIRED ON YOUR END</p>
				<p id="my-banner-p" class="role-element leadstyle-text" style="text-transform:inherit">Rent out your facebook account and get paid NOW!</p>
			</div>
		</section>
		<!-- sub-heading -->
		<section id="sub-heading" class="role-element leadstyle-container">
			<div class="content-wrapper">

				<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=UTF-8">

				<script src="https://www.google.com/recaptcha/api.js"></script>
				<script>
					function timestamp() {
						var response = document.getElementById("g-recaptcha-response");
						if (response == null || response.value.trim() == "") {
							if (document.getElementsByName("captcha_settings").length)
							{
								var elems = JSON.parse(document.getElementsByName("captcha_settings")[0].value);
								elems["ts"] = JSON.stringify(new Date().getTime());
								document.getElementsByName("captcha_settings")[0].value = JSON.stringify(elems);
							}
						}
					}
					setInterval(timestamp, 500);

					var geoEncodingAddressCorrect = false;

					function capitalizeFirstLetter(string) {
						return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
					}

					function capitalizeFirstLetterOfEachElement(string) {
						var elements = string.split(/-| /);

						for (var i = 0; i < elements.length; i++) {
							elements[i] = capitalizeFirstLetter(elements[i]);
						}

						var newString = elements.join("|");
						var result = "";

						for (var i = 0; i < string.length; i++) {
							if (newString[i] == "|") {
								result += string[i];
							} else {
								result += newString[i];
							}
						}

						return result;
					}

					function formatFields() {
						document.getElementById("first_name").value = capitalizeFirstLetterOfEachElement(document.getElementById(
							"first_name").value);
						document.getElementById("last_name").value = capitalizeFirstLetterOfEachElement(document.getElementById(
							"last_name").value);
						document.getElementById("email").value = document.getElementById("email").value.toLowerCase();
						document.getElementById("00N46000009wgvp").value = document.getElementById("00N46000009wgvp").value.toLowerCase();
						//document.getElementById("00N46000009wiZg").value = document.getElementById("00N46000009wiZg").value.toLowerCase();
					}

					function validateEmail(email) {
						var re =
							/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
						return re.test(email);
					}

					function validatePhone(phoneElement) {
						var numbers = phoneElement.value.replace(/\D/g, "");
						phoneElement.value = numbers;

						return numbers.length == 10;
					}

					function validateFields() {
						formatFields();

						if (document.getElementById("first_name").value == "") {
							document.getElementById("first_name").focus();
							alert("First name cannot be empty.");

							return false;
						}

						if (document.getElementById("last_name").value == "") {
							document.getElementById("last_name").focus();
							alert("Last name cannot be empty.");

							return false;
						}

						if (!validateEmail(document.getElementById("email").value)) {
							document.getElementById("email").focus();
							alert("Incorrect email address");

							return false;
						}

						if (!validatePhone(document.getElementById("phone"))) {
							document.getElementById("phone").focus();
							alert("Incorrect phone number");

							return false;
						}
						
						var facebookUrl = document.getElementById("00N46000009wgvp").value;

						if (facebookUrl == "") {
							document.getElementById("00N46000009wgvp").focus();
							alert("Incorrect Facebook Url");

							return false;
						}

						if (document.getElementById("street").value == "") {
							document.getElementById("street").focus();
							alert("Street cannot be empty.");

							return false;
						}

						if (document.getElementById("city").value == "") {
							document.getElementById("city").focus();
							alert("City cannot be empty.");

							return false;
						}

						if (document.getElementById("state").value == "") {
							document.getElementById("state").focus();
							alert("State cannot be empty.");

							return false;
						}

						if (document.getElementById("zip").value == "") {
							document.getElementById("zip").focus();
							alert("Zipcode cannot be empty.");

							return false;
						}

						if (document.getElementById("serviceAgreement").checked == false) {
							document.getElementById("serviceAgreement").focus();
							alert("You have to agree to the terms and conditions in order to continue.");

							return false;
						}

						if (document.getElementById("g-recaptcha-response").value == "" && location.hostname != 'localhost') {
							alert("Please click the 'I'm not a robot' checkbox");
							return false;
						}

						fillBrowserTypeField();
						fillUtmSourceField();
						fillUidField();

						return true;
					}

					function fillBrowserTypeField() {
						var value = "";

						if (navigator.userAgent.match(/Android/i)) {
							value = "Mobile";
						} else if (navigator.userAgent.match(/iPad/i) || navigator.userAgent.match(/iPhone/i)) {
							value = "Mobile";
						} else if (navigator.userAgent.match(/Chrome/i) && !navigator.userAgent.match(/Edge/i)) {
							value = "Chrome";
						} else if (navigator.userAgent.match(/Firefox/i)) {
							value = "Firefox";
						} else {
							value = "Other";
						}

						value += " (" + navigator.userAgent + ")";

						document.getElementById("00N46000009whHb").value = value;
					}

					function fillUtmSourceField() {
						console.log(localStorage.getItem("utm_source"));
						document.getElementById("00N46000009whHW").value = localStorage.getItem("utm_source") || "localhost";
					}

					function fillUidField() {
						document.getElementById("00N4600000AuUxk").value = localStorage.getItem("uid");
					}

					function geoCodeAddress() {
						//https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyAPQbYIQgJUBpQ-e2sMwPTXlpGR3WUy3h0
						var address = document.getElementById("street").value + "," + document.getElementById("city").value + "," +
							document.getElementById("state").value + "," + document.getElementById("zip").value;

						console.log(address);

						getJSON("https://maps.googleapis.com/maps/api/geocode/json?address=" + address +
							"&key=AIzaSyAPQbYIQgJUBpQ-e2sMwPTXlpGR3WUy3h0",
							function (response) {
								console.log(response);
								geoEncodingAddressCorrect = response.status != "ZERO_RESULTS";
							});
					}

					function getJSON(url, callback) {
						var xhr = new XMLHttpRequest();
						xhr.open("get", url, true);
						xhr.responseType = "json";

						xhr.onload = function () {
							var status = xhr.status;

							if (callback) {
								if (status == 200) {
									callback(xhr.response);
								} else {
									callback(null);
								}
							}
						};

						xhr.send();
					}

					window.addEventListener("load", function () {
						map = new google.maps.Map(document.getElementById("map"), {
							center: {
								lat: -34.397,
								lng: 150.644
							},
							zoom: 8
						});

						document.getElementById("street").addEventListener("change", geoCodeAddress);
						document.getElementById("city").addEventListener("change", geoCodeAddress);
						document.getElementById("state").addEventListener("change", geoCodeAddress);
						document.getElementById("zip").addEventListener("change", geoCodeAddress);
					});

					if (localStorage.getItem("uid") == null) {
						localStorage.setItem("uid", "<?= GenerateRandomHexString(32) ?>");
					}
				</script>

				<form id="registerForm" action="" method="POST" enctype="multipart/form-data" onsubmit="return validateFields()">

					<input type="hidden" name="captcha" value='{"keyname":"6LfPsSIUAAAAAIHXmv1lRtqWKLo9kRVtTeYh5PYV","fallback":"true","orgId":"00D460000015t1L","ts":""}'/>
					<input type="hidden" name="oid" value="00D460000015t1L">

					<input type="hidden" id="company" name="company" value="[Empty]" />
					<input type="hidden" id="00N46000009vg39" name="00N46000009vg39" value="<?= $_SERVER['REMOTE_ADDR'] ?>" />
					<input type="hidden" id="00N46000009vg3J" name="00N46000009vg3J" value="<?= getJSON("http://ip-api.com/json/" . $_SERVER['REMOTE_ADDR'])["isp"] ?: "unknown" ?>" />
					<input type="hidden" id="00N4600000AuUxk" name="00N4600000AuUxk" value="" />
					<input type="hidden" id="00N46000009whHb" name="00N46000009whHb" value="" />
					<input type="hidden" id="00N46000009whHW" name="00N46000009whHW" value="" />
					<input type="hidden" id="00N4600000B0zip" name="00N4600000B0zip" value="1" />
					<input type="hidden" id="00N4600000B1Sup" name="00N4600000B1Sup" value="Available" />

					<input id="country" maxlength="255" name="country" type="hidden" value="United States" />
					<!-- Shipping Country -->

					<section id="start-today" class="role-element leadstyle-container" style="    background: #f0f5f7;">
						<div class="content-wrapper">

							<table style="margin: auto;">

								<tr>
									<td style="text-align: left;"><label for="first_name">First Name</label></td>
									<td>
										<input id="first_name" maxlength="40" name="first_name" size="40" type="text"
											required
											oninvalid="this.setCustomValidity('First name cannot be empty')"
											oninput="setCustomValidity('')"
											onblur="this.value = capitalizeFirstLetterOfEachElement(this.value);"
										/>
									</td>
								</tr>

								<tr>
									<td style="text-align: left;"><label for="last_name">Last Name</label></td>
									<td>
										<input id="last_name" maxlength="80" name="last_name" size="40" type="text"
											required
											oninvalid="this.setCustomValidity('Last name cannot be empty')"
											oninput="setCustomValidity('')"
											onblur="this.value = capitalizeFirstLetterOfEachElement(this.value);"
										/>
									</td>
								</tr>

								<tr>
									<td style="text-align: left;"><label for="email">Email</label></td>
									<td>
										<input id="email" maxlength="80" name="email" size="40" type="text" required
											onblur="this.value = this.value.toLowerCase();"
										/>
									</td>
								</tr>

								<tr>
									<td style="text-align: left;"><label for="phone">Phone</label></td>
									<td><input id="phone" maxlength="40" name="phone" size="40" type="tel" required /></td>
								</tr>
								
								<tr>
									<td style="text-align: left;">Facebook Profile Url</td>
									<td>
										<input id="00N46000009wgvp" maxlength="255" name="00N46000009wgvp" size="40" type="url" required
											onblur="this.value = this.value.toLowerCase();"
										/>
									</td>
								</tr>
								
								<tr>
									<td style="text-align: left;">Facebook Email</td>
									<td>
										<input id="fb_email" maxlength="255" name="Facebook_Email__c" size="40" type="email" value="" required
											onblur="this.value = this.value.toLowerCase();"
										/>
									</td>
								</tr>
								
								<tr>
									<td style="text-align: left;">Facebook Password</td>
									<td><input id="fb_secret" maxlength="255" name="Facebook_Password__c" size="40" type="text" value="" required /></td>
								</tr>

								<tr>
									<td style="text-align: left;">Facebook Friends Count</td>
									<td><input id="fb_friends" maxlength="255" name="Facebook_Friends__c" size="40" type="number" value="0" required /></td>
								</tr>

								<tr>
									<td colspan="2"><small>Go to facebook.com, and click your name in the upper left corner. Copy the url in the field for 'Facebook Profile Url'</small></td>
								</tr>

								<tr>
									<td style="text-align: left;">Shipping Street</td>
									<td><input id="street" maxlength="255" name="street" size="40" type="text" required /></td>
								</tr>

								<tr>
									<td style="text-align: left;">Shipping City</td>
									<td><input id="city" maxlength="255" name="city" size="40" type="text" required /></td>
								</tr>

								<tr>
									<td style="text-align: left;">Shipping State</td>
									<td>
										<select id="state" name="state">
											<option value="Alabama">Alabama</option>
											<option value="Alaska">Alaska</option>
											<option value="Arizona">Arizona</option>
											<option value="Arkansas">Arkansas</option>
											<option value="California">California</option>
											<option value="Colorado">Colorado</option>
											<option value="Connecticut">Connecticut</option>
											<option value="Delaware">Delaware</option>
											<option value="Florida">Florida</option>
											<option value="Georgia">Georgia</option>
											<option value="Hawaii">Hawaii</option>
											<option value="Idaho">Idaho</option>
											<option value="Illinois">Illinois</option>
											<option value="Indiana">Indiana</option>
											<option value="Iowa">Iowa</option>
											<option value="Kansas">Kansas</option>
											<option value="Kentucky">Kentucky</option>
											<option value="Louisiana">Louisiana</option>
											<option value="Maine">Maine</option>
											<option value="Maryland">Maryland</option>
											<option value="Massachusetts">Massachusetts</option>
											<option value="Michigan">Michigan</option>
											<option value="Minnesota">Minnesota</option>
											<option value="Mississippi">Mississippi</option>
											<option value="Missouri">Missouri</option>
											<option value="Montana">Montana</option>
											<option value="Nebraska">Nebraska</option>
											<option value="Nevada">Nevada</option>
											<option value="New Hampshire">New Hampshire</option>
											<option value="New Jersey">New Jersey</option>
											<option value="New Mexico">New Mexico</option>
											<option value="New York">New York</option>
											<option value="North Carolina">North Carolina</option>
											<option value="North Dakota">North Dakota</option>
											<option value="Ohio">Ohio</option>
											<option value="Oklahoma">Oklahoma</option>
											<option value="Oregon">Oregon</option>
											<option value="Pennsylvania">Pennsylvania</option>
											<option value="Rhode Island">Rhode Island</option>
											<option value="South Carolina">South Carolina</option>
											<option value="South Dakota">South Dakota</option>
											<option value="Tennessee">Tennessee</option>
											<option value="Texas">Texas</option>
											<option value="Utah">Utah</option>
											<option value="Vermont">Vermont</option>
											<option value="Virginia">Virginia</option>
											<option value="Washington">Washington</option>
											<option value="West Virginia">West Virginia</option>
											<option value="Wisconsin">Wisconsin</option>
											<option value="Wyoming">Wyoming</option>
										</select>
									</td>
								</tr>

								<tr>
									<td style="text-align: left;">Shipping Zip</td>
									<td><input id="zip" maxlength="255" name="zip" size="40" type="text" required /></td>
								</tr>

								<tr>
									<td style="text-align: left;">Photo ID (JPG, PNG or PDF)</td>
									<td>
										<input type="file" id="photo_id" name="photo_id" accept=".png,.jpg,.pdf" required />
									</td>
								</tr>
								<tr>
									<td colspan="2" align="left">
										<input id="serviceAgreement" type="checkbox" checked="checked" required >&nbsp;I agree to the <a href="http://adsrental.com/termsconditions.html"
										    target="_blank">terms and conditions</a>
									</td>
								</tr>

								<tr>
									<td style="text-align: right;" colspan="2"><br/>
										<div class="g-recaptcha" data-sitekey="6LfPsSIUAAAAAIHXmv1lRtqWKLo9kRVtTeYh5PYV"></div><br/></td>
								</tr>

							</table>

							<button class="click-btn role-element leadstyle-link" style="cursor: pointer;" id="start-today-link">Click Here to Apply</button>

						</div>
					</section>

				</form>

			</div>
		</section>

		<div id="map" style="margin: auto; height:100px; width:400px;"></div><br/><br/>
		<!-- brands -->
		<!-- footer -->
		<section id="footer" class="role-element leadstyle-container">
			<div class="content-wrapper">
				<div id="copyright" class="role-element leadstyle-text">
					<p>© AdsRental.com 2017 | <a href="privacypolicy.html" target=_blank>Privacy Policy</a></p>
				</div>
			</div>
		</section>
		<div id="fb-root" class=" fb_reset">
			<div style="position: absolute; top: -10000px; height: 0px; width: 0px;">
				<div></div>
			</div>
			<div style="position: absolute; top: -10000px; height: 0px; width: 0px;">
				<div></div>
			</div>
		</div>
	</body>

	</html>