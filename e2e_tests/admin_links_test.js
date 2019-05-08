Feature('Admin links Test')

Scenario('links', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Leads')
    I.click('Proxy tunnel')
    I.see('RP999 proxy tunnel info')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Leads')
    I.click('Logs')
    I.see('RP999 logs')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Leads')
    I.click('pi.conf')
    I.click('Stats')
    I.see('Lead')    
    I.click('Admin')
    I.see('Dashboard')
    I.click('Leads')
    I.click('Fix address')
    I.see('Address for')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Leads')
    I.click('History')
    I.see('Select lead change to change')
    I.click('Home')
    I.click('Leads')
    I.click('Checks')
    I.see('Select Lead History Month to change')
    I.click('Home')
    I.click('Leads')
    I.click('Cost')
    I.see('Monthly payments')





     });