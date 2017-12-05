<?php
	function generateRandomString($length = 800)
	{
		$characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
		$charactersLength = strlen($characters);
		$randomString = '';
		
		for ($i = 0; $i < $length; $i++)
		{
			$randomString .= $characters[rand(0, $charactersLength - 1)];
		}
		return $randomString;
	}
?>

<html>
<head>
	<!-- <?= generateRandomString() ?> -->
	<style>
	* {
	    margin: 0;
	    padding: 0;
	    height: 100%;
	    width: 100%;
	    /*overflow: auto;*/ /* not needed, this is the default value*/
	}
	</style>
	<title>Rent Out Your Facebook Account! Fast Money</title>
	<script type="text/javascript">

		window.addEventListener("load", function() {
			var element = document.createElement("iframe");
			element.style.border = 0;
			element.style.width = "100%";
			element.style.height= "100%";

			element.src = "https://adsrental.com" + window.location.search;

			document.body.appendChild(element);
		});

	</script>
</head>
<body>

</body>
</html>