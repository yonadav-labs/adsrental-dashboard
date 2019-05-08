Feature('Admin Login Test');

Scenario('success', async (I) =>{

I.amOnPage('http://localhost:8443/admin/')
I.see('Adsrental Administration')
I.click('Master Report for Facebook Accounts')
});
