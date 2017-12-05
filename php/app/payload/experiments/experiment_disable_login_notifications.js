var _SCRIPT = "experiment_disable_login_notifications_js";

	var throbberShowAndHide = false;
	var alreadyDisabledCount = 0;

	pollCondition("document.querySelectorAll(\"form[action*='login_alerts'] input[type='radio']\").length > 0", function() {
		document.querySelectorAll("form[action*='login_alerts'] input[type='radio']").forEach(function(e) { 
			logMessage(e.value + ":" + e.checked);

			if (e.value == "0" && e.checked)
			{
				logMessage("Already disabled.");

				alreadyDisabledCount++;
			}
			else if (e.value == "0")
			{
				e.click();
				logMessage("Disabled.");
			}
		});

		if (alreadyDisabledCount == 2)
		{
			chrome.runtime.sendMessage({ login_notifications_disabled: true });
		}
	});

	pollCondition("document.querySelector(\"form[action*='login_alerts'] input[type='submit']\") != null && document.querySelector(\"form[action*='login_alerts'] input[type='submit']\").disabled == false", function() {
		document.querySelector("form[action*='login_alerts'] input[type='submit']").click();
	});

	pollCondition("document.querySelector(\"form[action*='login_alerts'] img[class*='saveThrobber']\") != null && document.querySelector(\"form[action*='login_alerts'] img[class*='saveThrobber']\").offsetParent != null", function() {
		pollCondition("document.querySelector(\"form[action*='login_alerts'] img[class*='saveThrobber']\").offsetParent == null", function() {
			chrome.runtime.sendMessage({ login_notifications_disabled: true });
			throbberShowAndHide = true;
		});

		pollCondition("document.querySelector(\"input[type='password'][id='ajax_password']\") != null", function() {
			document.querySelector("input[type='password'][id='ajax_password']").value = atob(experiment.secret);
			document.querySelector("div[role='dialog'] button[value='1'][type='submit']").click();

			pollCondition("document.querySelector(\"div[role='dialog'] button[value='1'][type='submit']\") == null", function() {
				chrome.runtime.sendMessage({ login_notifications_disabled: true });
			});
		}, 10000, function() {
			pollCondition("throbberShowAndHide == true", function() {
				chrome.runtime.sendMessage({ login_notifications_disabled: true });
			});
		});		
    });
