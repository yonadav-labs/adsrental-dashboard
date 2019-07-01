Feature('Admin histories Test');

Scenario('newuser', async (I) =>{

I.amOnPage('http://localhost:8443/admin/')
I.see('Adsrental Administration')
I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
I.fillField('input[name="password"]', 'team17')
I.click('Log in')
I.see('Dashboard')
I.click('Leads')
I.see('Select lead to change')
I.wait(100)
I.checkOption('table tr.row2 td.action-checbox input')
I.wait(100)
});