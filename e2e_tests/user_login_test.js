Feature('User Login Test');

Scenario('success', async (I) =>{
    I.amOnPage('http://localhost:8443/user/login/')
    I.see('User sign in')
    I.fillField('input[name="first_name"]', 'Vlad')
    I.fillField('input[name="last_name"]', 'Emelianow')
    I.fillField('input[name="postal_code"]', '5348489')
    I.click('Sign in')
    I.see('Lead')
    // I.wait(1000)
});

Scenario('error', async (I) =>{
    I.amOnPage('http://localhost:8443/user/login/')
    I.see('User sign in')
    I.fillField('input[name="first_name"]', 'Vlad')
    I.fillField('input[name="last_name"]', 'Emelianow')
    I.fillField('input[name="postal_code"]', '6348489')
    I.click('Sign in')
    I.see('User not found')
    // I.wait(1000)
});