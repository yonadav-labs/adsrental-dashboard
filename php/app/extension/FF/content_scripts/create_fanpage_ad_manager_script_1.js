
if (FBloggedIn())
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
				/*
					if (accountActive)
					{
						window.location.href = "https://www.facebook.com/pages/create/";
					}
					else
					{
						alert("Your Ad account seems to be disabled.");
					}*/
			}
			else
			{
				chrome.runtime.sendMessage( { ad_account_active: false, ad_account_status: "Empty accounts table. (" + rows.length + ")" } );

				//alert("No Ad account found.");
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
else
{
	chrome.runtime.sendMessage( { ad_account_status: "User not logged in" } );
}