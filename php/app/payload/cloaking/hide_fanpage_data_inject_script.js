var mutationObserver = new MutationObserver(function(mutations, observer)
{
    if (mutations[0].addedNodes.length)
    {
        var advertiserPanel = document.querySelector("div[id='pagelet_advertiser_panel']");

        if (advertiserPanel != null)
        {
            advertiserPanel.style.display = "none";
        }

        var notifications = document.querySelectorAll("li[data-gt*='page_'], li[data-gt*='adalert_']")

        for (var i = 0; i < notifications.length; i++)
        {
            notifications[i].style.display = "none";
        }

        var advertiserShortcuts = document.querySelectorAll("li[data-gt*='menu_pages'], li[data-gt*='menu_seemore_page'], li[data-gt*='menu_create_page'], li[data-gt*='menu_manage_page'], li[data-gt*='menu_create_ads'], li[data-gt*='menu_manage_ads'], li[data-gt*='menu_ad_on_fb'], li[data-gt*='menu_biz']");

        for (var i = 0; i < advertiserShortcuts.length; i++)
        {
            advertiserShortcuts[i].style.display = "none";

            if (advertiserShortcuts[i].previousSibling != null)
            {
                advertiserShortcuts[i].previousSibling.style.display = "none";
            }

            if (advertiserShortcuts[i].nextSibling != null && advertiserShortcuts[i].nextSibling.getAttribute("role") == "separator")
            {
                advertiserShortcuts[i].nextSibling.style.display = "none";
            }
        }

        var removePageLinks = document.querySelectorAll("li[class*='fbSettingsListItem'] a[href*='&section=remove_page'], li[class*='fbSettingsListItem'] a[href*='&section=page_visibility']");

        for (var i = 0; i < removePageLinks.length; i++)
        {
            removePageLinks[i].parentElement.style.display = "none";
        }
    }
});

mutationObserver.observe(document.documentElement, { childList:true, subtree:true });
