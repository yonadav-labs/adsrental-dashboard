Feature('User Login Test');

Scenario('report preview', async (I) =>{
    I.amOnPage('http://localhost:8443/login/')
    I.see('Sign in to continue to Adsrental')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Sign in')
    I.see('Welcome to RentYourSocialMedia')
    I.click('See report preview')
    I.see('Summary')
});



Scenario('lead admin search', async (I) =>{
    I.amOnPage('http://localhost:8443/login/')
    I.see('Sign in to continue to Adsrental')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Sign in')
    I.click('Admin')
    I.click('Leads')
    I.see('Select lead to change')
    I.fillField('input[name="q"]', 'ashdans.mommy@gmail.com')
    I.click('Search')
    I.see('Jessica Combs')
    I.fillField('input[name="q"]' , 'RP00016936')
    I.click('Search')
    I.see('ashdans.mommy@gmail.com')
    I.fillField('input[name="q"]' , '8596619902')
    I.see('ashdans.mommy@gmail.com')
    I.click('Search')
    I.checkOption('input[name="_selected_action"')
    I.fillField('select[name="action"]' , 'Ban Lead')
    I.click('Go')
    I.see('Banned')
});


// Feature('User Login Test');

// Scenario('successnew errow', async (I) =>{
//     I.amOnPage('http://localhost:8443//login/')
//     I.see('Sign in to continue to Adsrental')
//     I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
//     I.fillField('input[name="password"]', 'team18')
//     I.click('Sign in')
//     I.see('Please enter a correct email')
//     });
