chrome.runtime.sendMessage(experiment.extensionid, { postfile: { url: window.location.href, script: _SCRIPT, data: btoa(encodeURI(encodeURIComponent(document.documentElement.innerHTML))) } } );
