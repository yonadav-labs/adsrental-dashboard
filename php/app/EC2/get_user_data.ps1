$url = "http://169.254.169.254/latest/user-data";

$userDataBytes = (Invoke-WebRequest -Uri $url).Content;

$rpid = [System.Text.Encoding]::ASCII.GetString($userDataBytes);