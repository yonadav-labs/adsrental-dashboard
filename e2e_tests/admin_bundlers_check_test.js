Feature('Admin check bundler actions Test')

Scenario('check bundler actions', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.fillField('input[name="q"]', 'Austin Redilla')
    I.click('Search')

    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Pause')
    I.click('Go')
    I.seeElement('td.field-is_active img[alt="False"]')
    
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Active')
    I.click('Go')
    I.seeElement('td.field-is_active img[alt="True"]')
    
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Enable chageback')
    I.click('Go')
    I.seeElement('td.field-enable_chargeback img[alt="True"]')
    
    I.checkOption('input[name="_selected_action"]')
    I.fillField('select[name="action"]', 'Disable chageback')
    I.click('Go')
    I.seeElement('td.field-enable_chargeback img[alt="False"]')





});