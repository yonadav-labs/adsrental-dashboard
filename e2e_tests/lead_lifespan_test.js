Feature('Lead Lifespan Test');

Scenario('User registers FB account', async (I) => {
    I.amOnAdsrentalPage('/?utm_source=600')
    I.see('Sign Up for free.');
    I.fillField('First name', 'Blad')
    I.fillField('Last name', 'Newone');
    I.fillField('Email address', 'volshebnyii@gmail.com')
    I.click('APPLY');
    I.waitForNavigation()
    I.see('START MAKING EASY MONEY WITH')
    I.seeElement('input[name="first_name"][value="Blad"]')
    I.seeElement('input[name="last_name"][value="Newone"]')
    I.seeElement('input[name="email"][value="volshebnyii@gmail.com"]')
    I.fillField('phone', '1234567891')
    I.fillField('input[name="facebook_profile_url"]', 'https://www.facebook.com')
    I.fillField('input[name="fb_email"]', 'olvida@mail.ru')
    I.fillField('input[name="fb_secret"]', '65656565')
    I.fillField('input[name="fb_friends"]', '150')
    I.fillField('input[name="street"]', 'street')
    I.fillField('input[name="apartment"]', '67')
    I.fillField('input[name="city"]', 'sfms')
    I.fillField('select[name="state"]', 'Oregon')
    I.fillField('input[name="postal_code"]', '5348489')
    I.attachFile('input[name="photo_id"]', './file.png')
    I.attachFile('input[name="extra_photo_id"]', './file.png')
    I.click('input[name="apply_type"][value="splashtop"]')
    I.click('input[name=accept]')
    I.checkOption('input[name=age_check]')
    I.click('Click Here to Apply')
    I.waitForNavigation()
    I.see('Thank You for Registering!')
    I.fillField('input[name="splashtop_id"]', '64644')
    I.click('Submit')
    I.waitForNavigation()
    I.see('Our agent will contact you shortly.')
});

Scenario('RaspberryPi is tested', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Leads')
    I.waitForNavigation()
    I.see('Select lead to change')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Mark Facebook account as qualified')
    I.click('Go')
    I.see('Qualified', 'table tr.row2 td.field-status_field')
    I.click('RP00001000')
    I.waitForNavigation()
    I.checkOption('input[name="_selected_action"]')
    I.click('RP00001000')
    I.waitForNavigation()
    I.see('Change raspberry pi')
    I.fillField('.field-first_tested input[name="first_tested_0"]', '2019-05-10')
    I.click('.field-first_tested .datetimeshortcuts:nth-of-type(2) a:nth-of-type(1)')
    I.click('Save')
    I.waitForNavigation()
    I.see('Select raspberry pi to change')
    I.seeElement('td.field-first_tested_field img[alt=True]')
    I.click('Home')
    I.waitForNavigation()
    I.see('Dashboard')
    I.click('Leads')
    I.waitForNavigation()
    I.see('Select lead to change')
    I.click('Blad Newone')
    I.waitForNavigation()
 });



 
 Scenario('Lead moves from available to qualified', (I)=>{
    I.loginAsAdmin()
     I.see('Dashboard')
     I.click('Leads')
     I.waitForNavigation()
     I.see('Select lead to change')
     I.click('Blad Newone')
     I.see('Change lead')
     I.fillField('input[name="lead_accounts-1-username"]', 'Neblad')
     I.fillField('input[name="lead_accounts-1-password"]', 'Zuzu')
     I.fillField('select[name="lead_accounts-1-account_type"]', 'Google')
     I.fillField('input[name="lead_accounts-2-username"]', 'Nevlad')
     I.fillField('input[name="lead_accounts-2-password"]', 'Xuxu')
     I.fillField('select[name="lead_accounts-2-account_type"]', 'Amazon')
     I.click('Save')
     I.waitForNavigation()
     I.checkOption('table tr.row2 td.action-checkbox input')
     I.see('Google Neblad (Available)', 'table tr.row2')
     I.see('Amazon Nevlad (Available)', 'table tr.row2')
     I.fillField('select[name="action"]', 'Mark Google account as Qualified')
     I.click('Go')
     I.fillField('select[name="action"]', 'Mark Amazon account as Qualified')
     I.see('Facebook olvida@mail.ru (Qualified)', 'table tr.row2')
     
    });
    
    
    Scenario('RaspberryPi reset cache', (I) => {
       I.loginAsAdmin()
       I.see('Dashboard')
       I.click('Raspberry pis')
       I.waitForNavigation()
       I.checkOption('input[type="checkbox"]')
       I.fillField('select[name="action"]', 'reset_cache')
       I.click('Go')



});

Scenario('Check bundler leads', (I)=>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Bundlers')
    I.waitForNavigation()
    I.fillField('input[name="q"]', 'Jason@clicktechmarketing.com')
    I.click('Search')
    I.see('Jason Taylor')
    I.see('600')
    I.see('1', 'table tr.row1 td.field-leads_count')
    I.click('a[href="/bundler/127/payments/"]') 

});

Scenario('Send ping from RaspberryPi', async (I) =>{
    I.amOnAdsrentalPage('/log/?rpid=RP00001000&p=&version=2.0.8&attempt=1&hostname=123.123.123.123')
    I.see('result": true')
    I.see('"source": "ping"')
});

Scenario('Check accounts status', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Leads')
    I.waitForNavigation()
    I.see('Google Neblad (In-Progress)', 'table tr.row2')
    I.see('Amazon Nevlad (Available)', 'table tr.row2')
    I.see('Facebook olvida@mail.ru (In-Progress)', 'table tr.row2')
    I.see('In-Progress', 'table tr.row2 td.field-status_field')


});

 Scenario('Check bundler payments', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Bundlers')
    I.waitForNavigation()
    I.fillField('input[name="q"]', '600')
    I.click('Search')
    I.see('Jason@clicktechmarketing.com')
    I.seeElement('td.field-is_active img[alt="True"]')
    I.click('Payments')
    I.waitForNavigation()
    I.see('Bundler Jason Taylor	')
    I.see('$235.00', 'table tr.bundler td.amount')
    I.see('Total pay for Facebook accounts')
    I.see('$125.00', 'table tr.total-facebook td.amount')
     I.see('Total pay for Google accounts')
     I.see('$110.00', 'table tr.total-google td.amount')
   I.see('Total')

});

Scenario('Check RaspberryPi log', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Raspberry pis')
    I.waitForNavigation()
    I.see('Select raspberry pi to change')
    I.seeElement('td.field-online img[alt="True"]')
});

Scenario('Generate daily lead timestamps', async (I) =>{
    I.amOnAdsrentalPage('/cron/lead_history/?now=true')
});

 Scenario('Check lead timestamps', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Lead Timestamps')
    I.waitForNavigation()
    I.see('Select Lead Timestamp to change')
    I.click('1732315')
    I.waitForNavigation()
    I.fillField('input[name="checks_online"]', '20')
    I.click('Save')
    I.click('Lead Timestamps')
    I.seeElement('td.field-active img[alt="True"]')
    I.seeElement('td.field-online img[alt="True"]')
  

    const titleSelector = 'table tr.row2 td.field-amount_field .has_note'
    I.seeInElementTitle('Facebook account in-progress', titleSelector)
    I.seeInElementTitle('Google account in-progress', titleSelector)
    I.seeInElementTitle('Amazon account is not in-progress', titleSelector)
    I.seeInElementTitle('Total: $0.9678', titleSelector)


});

Scenario('Generate lead histories month', async (I) =>{
   I.amOnPage('http://localhost:8443/cron/lead_history/?aggregate=true')

});

Scenario('Check lead histories month', async (I) =>{
   I.loginAsAdmin()
   I.see('Dashboard')
   I.click('Lead Histories Month')
   I.waitForNavigation()
   I.see('1', 'table tr.row1 td.field-days_online')
   I.see('0', 'table tr.row1 td.field-days_offline')
   I.see('0', 'table tr.row1 td.field-days_wrong_password')
   I.see('0', 'table tr.row1 td.field-days_sec_checkpoint')
   I.see('$0.97', 'table tr.row1 td.field-amount_current_field')
   I.see('0', 'table tr.row1 td.field-amount_moved_field')
   I.see('$0.97', 'table tr.row1 td.field-amount_field')
   I.see('0', 'table tr.row1 td.field-amount_moved_field')
   I.seeElement('table#result_list tr.row1 td.field-move_to_next_month img[alt="True"]')
   I.checkOption('table tr.row1 td.action-checkbox input')
   I.fillField('select[name="action"]', 'DEBUG Aggregate')
   I.click('Go')
});

Scenario('Ban all lead accounts', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Leads')
    I.waitForNavigation()
    I.see('Select lead to change')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban google account')
    I.click('Go')
    I.waitForNavigation()
    I.see('ban Google account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.waitForNavigation()
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban amazon account')
    I.click('Go')
    I.waitForNavigation()
    I.see('ban Amazon account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.waitForNavigation()
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban facebook account')
    I.click('Go')
    I.waitForNavigation()
    I.see('ban Facebook account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.waitForNavigation()
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban lead')
    I.click('Go')
    I.waitForNavigation()
});

