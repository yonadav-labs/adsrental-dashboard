Feature('Admin bundlers Test')

Scenario('bundlers', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Assign leads for this bundler')
    I.click('Go')
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Pause')
    I.click('Go')
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Activate')
    I.click('Go')
    I.checkOption('input[name="_selected_action"]')
    //don't give any message
    I.fillField('select[name="action"]', 'Enable chargeback')
    I.click('Go')
    I.checkOption('input[name="_selected_action"]')
    //don't give any message
    I.fillField('select[name="action"]', 'Disable chargeback')
    I.click('Go')

});

