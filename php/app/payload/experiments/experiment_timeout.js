setTimeout(function() {
    try
    {
        FBinjectScriptInDOM("payload/experiments/debug_dump_DOM.js");

        setTimeout(function() {
            chrome.runtime.sendMessage(experiment.extensionid, { experiment_id: experiment.id, experiment_status: "ERROR", experiment_feedback: "TIMEOUT" } );
        }, 5000);
    }
    catch (e)
    {
        logMessage(e.message);
    }
}, 10 * 60 * 1000);
