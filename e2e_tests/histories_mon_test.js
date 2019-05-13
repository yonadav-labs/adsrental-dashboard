Feature('Admin histories Test');

Scenario('histories', async (I) =>{

I.amOnPage('http://localhost:8443/admin/')
I.see('Adsrental Administration')
I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
I.fillField('input[name="password"]', 'team17')
I.click('Log in')
I.see('Dashboard')
I.click('Lead Histories Month')
I.checkOption('input[id="action-toggle"]')
I.fillField('select[name="action"]', 'Export csv')
I.click('Go')
// I.checkDow/nLoadUrl(url[1],{size:75,type:'text/csv'})
// I.fillField('select[name="action"]', 'DEBUG: Aggregate')
// I.click('Go')


I.see('12', 'table tr.row1 td.field-days_online')
I.see('0', 'table tr.row1 td.field-days_offline')
I.click('table tr.row1 td.field-links a')
I.see('Timestamp')
I.checkOption('table tr.row1 td.action-checkbox input')
I.checkOption('table tr.row2 td.action-checkbox input')
I.checkOption('table tr.row2 td.action-checkbox input')
I.fillField('select[name="action"]', 'Mark as offline')
I.click('Go')
I.seeElement('td.field-active img[alt="False"]')
I.seeElement('td.field-online img[alt="False"]')
I.seeElement('td.field-wrong_password img[alt="False"]')
I.seeElement('td.field-security_checkpoint img[alt="False"]')
I.click('Home')
I.see('Dashboard')
I.click('Lead Histories Month')
I.see('Select Lead History Month to change')
I.checkOption('input[id="action-toggle"]')
I.fillField('select[name="action"]', 'DEBUG: Aggregate')
I.click('Go')
I.see('10', 'table tr.row1 td.field-days_online')
I.see('2', 'table tr.row1 td.field-days_offline')

});
    