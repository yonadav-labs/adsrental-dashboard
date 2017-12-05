var _SCRIPT = "helper_functions_js";

	///// GLOBAL DOM SELECTORS ///////////

	var postTimestampSelector = "document.querySelectorAll(\"[class='timestampContent']\")";
	var lastPostTimestampSelector = postTimestampSelector + "[0]";
	var lastPostLinkSelector = lastPostTimestampSelector + ".parentNode.parentNode.href";
	var postTimestampLengthSelector = postTimestampSelector + ".length";

	var composerSelectors = ["div[data-testid='react-composer-root'] textarea", "div[aria-controls*='js_'] div div div em", "div[data-testid='react-composer-root'] div div div div div div", "div[data-testid='react-composer-root'] a"];
	
	////// PROTOTYPE OVERRIDES /////////////

	function createTimeoutFunction(element, callback)
	{
		return function() {
			element.click();

			if (callback)
			{
				callback();
			}
		}
	}

	Element.prototype.delayClick = function(delay, callback) { setTimeout(createTimeoutFunction(this, callback), delay); };

	///////////////////////////////////////////////////////////////////////////

	function isString(x)
	{
		return Object.prototype.toString.call(x) === "[object String]";
	}

	function isFormData(x)
	{
		return Object.prototype.toString.call(x) === "[object FormData]";
	}

	function logMessage(message)
	{
		console.log(message);

		if (typeof extensionid !== "undefined")
		{
			chrome.runtime.sendMessage(extensionid, { message: message });	
		}
		else if (typeof sessionData !== "undefined")
		{
			chrome.runtime.sendMessage(sessionData.extensionid, { message: message });
		}
		else if (typeof experiment !== "undefined" && experiment.extensionid)
		{
			chrome.runtime.sendMessage(experiment.extensionid, { message: message });
		}
		else
		{
			try
			{
				// Try messaging w/o id
				chrome.runtime.sendMessage({ message: message });
			}
			catch (e)
			{
			}
		}
	}

	///////////////////////////////////////////////////////////////////////////

	function getReactObject(domElement)
	{
	    for (var key in domElement)
	    {
	        if (key.startsWith("__reactInternalInstance$"))
	        {
	            var compInternals = domElement[key]._currentElement;

	            if (compInternals == null)
	            {
	            	return { props: domElement[key].memoizedProps };
	            }

	            var compWrapper = compInternals._owner;
	            var comp = compWrapper._instance;

	            return comp;
	        }
	    }

    	return null;
	}

	function prepareJSONforInject(jsonString)
	{
		return jsonString.replace(/\n/g, "\\\\n")
	                     .replace(/\'/g, "\\'")
	                     .replace(/\`/g, "\\`")
	                     .replace(/\r/g, "\\\\r");
	}

	function FBinjectSessionData()
	{
		var cleanJSON = prepareJSONforInject(JSON.stringify(sessionData));

		var setDataScript = document.createElement("script");
		setDataScript.text = "var sessionData = " + cleanJSON + ";";
		setDataScript.onload = function() { this.remove(); };

		(document.head || document.documentElement).appendChild(setDataScript);	
	}

	function FBinjectExperiment()
	{
		var cleanJSON = prepareJSONforInject(JSON.stringify(experiment));

		var setDataScript = document.createElement("script");
		setDataScript.text = "var experiment = " + cleanJSON + ";";
		setDataScript.onload = function() { this.remove(); };

		(document.head || document.documentElement).appendChild(setDataScript);		
	}

	function FBinjectScriptInDOM(filename)
	{
		var s = document.createElement("script");
		s.type = "text/javascript";
		s.src = chrome.extension.getURL(filename);
		s.onload = function() { this.remove(); };

		(document.head || document.documentElement).appendChild(s);
	}

	function FBinjectCodeInDOM(code)
	{
		var s = document.createElement("script");
		s.type = "text/javascript";
		s.text = code;
		s.onload = function() { this.remove(); };

		(document.head || document.documentElement).appendChild(s);		
	}

	function FBloggedIn()
	{
		var loginForm = document.getElementById("login_form");
		var loggedOutDiv = document.querySelector("div[class='loggedout_menubar_container']");

		return loginForm == null && loggedOutDiv == null;
	}

	function FBgetAdAccountId()
	{
		var actRegex = /[?&]act=([\d]+)/;
		var aElements = document.querySelectorAll("a");

		for (var i = 0; i < aElements.length; i++)
		{
			var e = aElements[i];

			if (e.href.match(actRegex))
			{
				return e.href.match(actRegex)[1];
			}
		}

		return null;
	}

	function FBgetProfileId()
	{
		var profileImage = document.querySelector("img[id*='profile_pic_header']");

		if (profileImage != null && profileImage.id != "")
		{
			try
			{
				var result = profileImage.id.substring(profileImage.id.lastIndexOf("_") + 1);

				return result;
			}
			catch (e)
			{
			}
		}
/*
		var profileRegex = /&referrer_profile_id=([\d]+)/;
		var aElements = document.querySelectorAll("a");

		for (var i = 0; i < aElements.length; i++)
		{
			var e = aElements[i];

			if (e.href.match(profileRegex))
			{
				return e.href.match(profileRegex)[1];
			}
		}*/

		return null;
	}

	/////////////// Multiple selector helpers /////////////////////////////////

	function selectorArrayToNullCheckCondition(selectorArray)
	{
		return "document.querySelector(\"" + selectorArray.join("\") != null || document.querySelector(\"") + "\") != null";
	}

	function getObjectBySelectors(selectorArray)
	{
		for (var i = 0; i < selectorArray.length; i++)
		{
			if (document.querySelector(selectorArray[i]) != null)
			{
				return document.querySelector(selectorArray[i]);
			}
		}

		return null;
	}

	function searchUpForTagName(element, tagName)
	{
		if (element.parentNode != null && element.parentNode.tagName.toLowerCase() == tagName.toLowerCase())
		{
			return element.parentNode;
		}
		else if (element.parentNode == null)
		{
			return null;
		}

		return searchUpForTagName(element.parentNode, tagName);
	}

	///////////////////////////////////////////////////////////////////////////

	function pollCondition(condition, callback, timeoutValue = null, timeoutCallback = null)
	{
		if (timeoutValue != null)
		{
			logMessage("pollCondition tick: " + timeoutValue);
			
			if (timeoutValue <= 0)
			{
				logMessage("pollCondition timeoutCallback");
				
				timeoutCallback();
				return;
			}
		}

		if (!eval(condition))
		{
			setTimeout(function() { pollCondition(condition, callback, timeoutValue != null ? (timeoutValue - 500) : null, timeoutCallback); }, 500);
			return;
		}

		logMessage("pollCondition met: " + condition);

		callback();
	}

	function pollValueHasChanged(valueExpression, callback, timeoutValue = null, timeoutCallback = null)
	{
		pollCondition(valueExpression + " != " + eval(valueExpression), callback, timeoutValue, timeoutCallback);
	}

	function b64toByteArray(b64Data, sliceSize)
	{
		sliceSize = sliceSize || 512;

		var byteCharacters = atob(b64Data);
		var byteArrays = [];

		for (var offset = 0; offset < byteCharacters.length; offset += sliceSize)
		{
			var slice = byteCharacters.slice(offset, offset + sliceSize);

			var byteNumbers = new Array(slice.length);

			for (var i = 0; i < slice.length; i++)
			{
				byteNumbers[i] = slice.charCodeAt(i);
			}

			var byteArray = new Uint8Array(byteNumbers);

			byteArrays.push(byteArray);
		}

		return byteArrays;
	}

	function postData(url, formData, withCredentials, callback)
	{
	    var xhr = new XMLHttpRequest();
	    xhr.open("post", url, true);
		xhr.withCredentials = withCredentials; // NEEDED for adding cookies

		//THIS ENABLED PRE FLIGHT
		//xhr.setRequestHeader('X_FB_BACKGROUND_STATE', '1');

	    xhr.onload = function() {
			var status = xhr.status;

			if (callback)
			{
				if (status == 200)
				{
					callback(null, xhr.response);
				}
				else
				{
					callback(status, null);

					console.log(xhr.response);
				}
			}
		};

	    xhr.send(formData);
	}

	function findElementByText(selector, text)
	{
		var result = [];

		for (const a of document.querySelectorAll(selector))
		{
			if (a.textContent.includes(text))
			{
				result.push(a);
			}
		}

		return result;
    }
