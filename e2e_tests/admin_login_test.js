Feature('Admin Login Test');

Scenario('success', async (I) =>{
I.amOnPage('http://localhost:8443/admin/login/?next=/admin/')
I.see('Adsrental Administration')
I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
I.fillField('input[name="password"]', 'team17')
I.click('Log in')
I.see('Adsrental Administration')
});


Feature('Admin Login Test');

Scenario('success error', async (I) =>{
I.amOnPage('http://localhost:8443/admin/login/?next=/admin/')
I.see('Adsrental Administration')
I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
I.fillField('input[name="password"]', 'team18')
I.click('Log in')
I.see('Please enter the correct')
});