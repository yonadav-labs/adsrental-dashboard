Feature('Admin histories Test');

Scenario('timestamps', async (I) =>{

I.amOnPage('http://localhost:8443/admin/')
I.see('Adsrental Administration')
I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
I.fillField('input[name="password"]', 'team17')
I.click('Log in')
I.see('Dashboard')
I.click('Lead Timestamps')
I.see('Select Lead Timestamp to change')
I.checkOption('input[type="checkbox"]')
I.fillField('select[name="action"]', 'Mark as onlain')
I.click('Go')
// I.wait(100)
I.seeElement('td.field-active img[alt="True"]')
I.checkOption('input[type="checkbox"]')
I.fillField('select[name="action"]', 'Mark as offlain')
I.click('Go')
// I.wait(100)
I.seeElement('td.field-active img[alt="False"]')



});