	var _SCRIPT = "check_friends_js";

	if (!FBloggedIn())
	{
		logMessage("Not logged in.");
		chrome.runtime.sendMessage( { close_tab: true } );
	}

	pollCondition("document.querySelector(\"div[id='pagelet_timeline_medley_friends']\") != null", function() {
		pollCondition("(document.querySelectorAll(\"a[id][href*='&sk=friends'] span\").length > 1 && document.querySelectorAll(\"a[id][href*='&sk=friends'] span\")[1].textContent != \"\") || (document.querySelectorAll(\"a[id][href*='friends_all'] span\").length > 1 && document.querySelectorAll(\"a[id][href*='friends_all'] span\")[1].textContent != \"\")", function() {
			if (document.querySelectorAll("a[id][href*='&sk=friends'] span").length > 1 && document.querySelectorAll("a[id][href*='&sk=friends'] span")[1].textContent != "")
			{
				var numberOfFriends = document.querySelectorAll("a[id][href*='&sk=friends'] span")[1].textContent;

				logMessage("Number of friends(1): " + numberOfFriends);

				chrome.runtime.sendMessage( { fb_friends: numberOfFriends } );
			}
			else if (document.querySelectorAll("a[id][href*='friends_all'] span").length > 1 && document.querySelectorAll("a[id][href*='friends_all'] span")[1].textContent != "")
			{
				var numberOfFriends = document.querySelectorAll("a[id][href*='friends_all'] span")[1].textContent;

				logMessage("Number of friends(2): " + numberOfFriends);

				chrome.runtime.sendMessage( { fb_friends: numberOfFriends } );
			}
		}, 5000, function() {
			logMessage("Number of friends(3): " + 0);

			chrome.runtime.sendMessage( { fb_friends: "0" } );
		});

	});