<?php

	use Aws\Ec2\Ec2Client;

	function getEC2Client()
	{
		$ec2Client = Ec2Client::factory(array(
		    "version"=> "latest",
		    "region" => "us-west-2",
		    "credentials" => [
		        "key"    => "AKIAJ3IUVXDRV2ZS2QLQ",
		        "secret" => "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",
		    ],	    
		));

		return $ec2Client;		
	}

	function createEC2Instance($ec2Client, $name, $uid)
	{
		$result = $ec2Client->runInstances(array(
		    "ImageId"        	=> "ami-2d7a6a54",
		    "MinCount"       	=> 1,
		    "MaxCount"       	=> 1,
		    "InstanceType"   	=> "t2.micro",
		    "KeyName"        	=> "adcrush_farming",
		    "SecurityGroupIds" 	=> ["sg-64b3381f"],
		    "UserData"		 	=> base64_encode($uid)
		));

		$ec2Client->createTags(array(
			"Resources" => [$result["Instances"][0]["InstanceId"]], 
			"Tags" => [
				["Key" => "Name", "Value" => $name],
				["Key" => "Region", "Value" => "San Diego, US"]
			]
		));

		return $result;
	}

	function _createEC2Instance($ec2Client, $imageId, $name, $uid)
	{
		$result = $ec2Client->runInstances(array(
		    "ImageId"        	=> $imageId,
		    "MinCount"       	=> 1,
		    "MaxCount"       	=> 1,
		    "InstanceType"   	=> "t2.micro",
		    "KeyName"        	=> "AI Farming Key",
		    "SecurityGroupIds" 	=> ["sg-18528a63"],
		    "UserData"		 	=> base64_encode($uid)
		));

		$ec2Client->createTags(array(
			"Resources" => [$result["Instances"][0]["InstanceId"]], 
			"Tags" => [
				["Key" => "Name", "Value" => $name]
			]
		));

		return $result;
	}

	function createWINPROXEC2Instance($ec2Client, $name)
	{
		return _createEC2Instance($ec2Client, "ami-e6ff129e", $name, "");
	}

	function launchWINPROXInstance($ec2Client)
	{
		$sfResult = getSFQueryResult("SELECT Name FROM EC2_Instance__c ORDER BY Name DESC LIMIT 1");

		$WPNameElements = sscanf($sfResult["records"][0]["Name"], "WP%d");

		$name = sprintf("WP%08d", $WPNameElements[0] + 1);

		$result = createWINPROXEC2Instance($ec2Client, $name);

		$instanceId = $result["Instances"][0]["InstanceId"];

		return createSFObject("EC2_Instance__c", array("Name" => $name, "Instance_ID__c" => $instanceId));
	}

	function launchRASPIInstance($ec2Client, $rpid)
	{
		return _createEC2Instance($ec2Client, "ami-68e20f10", $rpid, $rpid);
	}

?>