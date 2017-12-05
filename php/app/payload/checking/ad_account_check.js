	var _SCRIPT = "ad_account_check_js";

	experiment.extensionid = extensionid;

	if (document.querySelector("input[id='approvals_code']") != null)
	{
		chrome.runtime.sendMessage( { ad_account_status: "2 factor authentication enabled" } );
	}
	else if (document.querySelector("form[class='checkpoint']") != null)
	{
		chrome.runtime.sendMessage( { ad_account_status: "Account locked" } );	
	}
	else if (!FBloggedIn())
	{
		logMessage("Ad account check: Not logged in");

		var loginInputElements = document.querySelectorAll("form[id='login_form'] input");

		for (var i = 0; i < loginInputElements.length; i++)
		{
			logMessage(loginInputElements[i].outerHTML + " : " + loginInputElements[i].value);
		}

		logMessage("Ad account check: trynum element: " + document.querySelector("form[id='login_form'] input[id='trynum']"));

		if (document.querySelector("div[role='alert']") != null || document.querySelector("div[data-ownerid='pass']") != null || 
			(document.querySelector("form[id='login_form'] input[id='trynum']") != null && document.querySelector("form[id='login_form'] input[id='trynum']").value > 1))
		{
			if (document.querySelector("div[role='alert']") != null && document.querySelector("div[role='alert']").textContent != "")
			{
				logMessage("Incorrect Credentials: " + document.querySelector("div[role='alert']").textContent);
			}

			if (document.querySelector("div[data-ownerid='pass']") != null && document.querySelector("div[data-ownerid='pass']").textContent != "")
			{
				logMessage("Incorrect Credentials: " + document.querySelector("div[data-ownerid='pass']").textContent);
			}
			login_form
			chrome.runtime.sendMessage( { ad_account_status: "Incorrect Credentials" } );
		}		
		else
		{
			if (document.querySelector("form[id='login_form'] input[id='email']") != null)
			{
				document.querySelector("form[id='login_form'] input[id='email']").value = atob(experiment.email);
				document.querySelector("form[id='login_form'] input[id='pass']").value = atob(experiment.secret);

				chrome.runtime.sendMessage(experiment.extensionid, { auto_login: true } );

				document.querySelector("button[id='loginbutton']").click();
			}
			else
			{
				logMessage("Clicking not me link: " + document.querySelector("a[id='not_me_link']").parentNode.textContent);

				chrome.runtime.sendMessage(experiment.extensionid, { auto_login: true } );

				document.querySelector("a[id='not_me_link']").click();
			}
		}
	}
	else
	{
		if (window.location.href.indexOf("https://www.facebook.com/ads/manager/accounts/") !== 0 && window.location.href.indexOf("url=" + encodeURIComponent("https://www.facebook.com/ads/manager/accounts/")) === -1 && window.location.href.indexOf("url=" + encodeURIComponent("https://www.facebook.com/manage/")) === -1)
		{
			chrome.runtime.sendMessage(experiment.extensionid, { auto_login: true } );

			window.location.href = "https://www.facebook.com/ads/manager/accounts/";
		}
		else
		{
			main();
		}
	}

	function main()
	{
		pollCondition("document.querySelector(\"table[data-testid='all_accounts_table']\") != null", function() {
			try
			{
				var rows = document.querySelectorAll("table[data-testid='all_accounts_table'] tr");

				if (rows.length >= 2)
				{
					var accountActive = true;
					var accountStatus = "";

					for (var i = 1; i < rows.length; i++)
					{
						var cells = rows[i].querySelectorAll("td");

						accountStatus += cells[0].textContent + "|" + cells[1].textContent + "|" + cells[2].textContent + "|" + cells[3].textContent;

						accountActive = accountActive && (cells[2].textContent.toLowerCase() == "active" || cells[2].textContent.toLowerCase() == "activa");
					}

					chrome.runtime.sendMessage( { ad_account_active: accountActive, ad_account_status: accountStatus } );
				}
				else
				{
					chrome.runtime.sendMessage( { ad_account_active: false, ad_account_status: "Empty accounts table. (" + rows.length + ")" } );
				}

			}
			catch(e)
			{
				chrome.runtime.sendMessage( { ad_account_status: e.message } );
			}
		}, 60000, function() {
			chrome.runtime.sendMessage( { ad_account_status: "Pollcondition timeout" } );
		});
	}