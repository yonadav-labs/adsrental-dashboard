Feature('Lead daily');

Scenario('timestamps', async (I) =>{
I.loginAsAdmin()
I.see('Dashboard')
I.amOnPage('http://localhost:8443/cron/lead_history/?now=true')
I.click('Lead Timestamps')
I.see('Select Lead Timestamp to change')
I.click('1732315')

});
