if (typeof background_request_handler_js == "undefined")
{
    background_request_handler_js = true;

    chrome.webRequest.onBeforeRequest.addListener(function(details) {
        // Ignore all requests to our server
        if (details.url.indexOf(serverBaseUrl) !== -1)
        {
            return;
        }

        if (logRequests)
        {
            sendLogMessage(">>> REQUEST: " + details.url + ":" + details.method);

            //console.log(details);
        }			

        if (cancelRequest != null)
        {
            for (var i = 0; i < cancelRequest.length; i++)
            {
                if (details.url.indexOf(cancelRequest[i]) !== -1)
                {
                    sendLogMessage(">>> CANCELLING: " + details.url);

                    cancelRequest = null;

                    return { cancel: true };
                }
            }
        }
        else if (cancelRequest != null)
        {
            sendLogMessage(">>> NOT CANCELLING: " + details.url);				
        }

        if (replaceRequest != null)
        {
            for (var i = 0; i < replaceRequest.param1.length; i++)
            {
                if (details.url.indexOf(replaceRequest.param1[i]) !== -1)
                {
                    sendLogMessage(">>> REPLACING: " + details.url);

                    var newUrl = details.url.replace(replaceRequest.param1[i], replaceRequest.param2);

                    replaceRequest = null;

                    return { redirectUrl: newUrl };
                }
            }
        }
        else if (replaceRequest != null)
        {
            sendLogMessage(">>> NOT REPLACING: " + details.url);
        }
    },
    { urls: ["<all_urls>"] }, ["blocking"]);
}
