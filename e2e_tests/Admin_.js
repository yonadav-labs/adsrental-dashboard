Feature('Admin Login Test');

Scenario('success', async (I) =>{

I.amOnPage('http://localhost:8443/admin/')
I.see('Adsrental Administration')
I.click('Master Report for Facebook Accounts')
I.fillField('select[name="action"]', 'Ban google account')
I.click('Go')
I.see('Choose reason to ban Google account')
I.fillField('textarea[name="note"]need b')
I.click('Ban')
