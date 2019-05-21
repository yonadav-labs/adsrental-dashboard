Feature('Lead Lifespan Test');

Scenario('signup', async (I) => {
    I.amOnPage('http://localhost:8443/?utm_source=600');
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
    I.see('Our agent will contact you shortly.')
});

Scenario('qualify', async (I) =>{
    I.amOnPage('http://localhost:8443/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Leads')
    I.waitForNavigation()
    I.see('Select lead to change')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Mark Facebook account as qualified')
    I.click('Go')
    I.see('Qualified', 'table tr.row2 td.field-status_field')
    I.click('RP00001000')
    I.checkOption('input[name="_selected_action"]')
    I.click('RP00001000')
    I.see('Change raspberry pi')
    // I.click('.field-first_tested .datetimeshortcuts:nth-of-type(1) a:nth-of-type(1)')
    I.fillField('.field-first_tested input[name="first_tested_0"]', '2019-05-10')
    I.click('.field-first_tested .datetimeshortcuts:nth-of-type(2) a:nth-of-type(1)')
    I.click('Save')
    I.see('Select raspberry pi to change')
    I.seeElement('td.field-first_tested_field img[alt=True]')
    I.click('Home')
    I.see('Dashboard')
    I.click('Leads')
    I.see('Select lead to change')
    I.click('Blad Newone')
 });



 
 Scenario('checkaccount', (I)=>{
     I.amOnPage('http://localhost:8443/app/admin/')
     I.see('Adsrental Administration')
     I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
     I.fillField('input[name="password"]', 'team17')
     I.click('Log in')
     I.see('Dashboard')
     I.click('Leads')
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
     I.checkOption('table tr.row2 td.action-checkbox input')
     I.see('Google Neblad (Available)', 'table tr.row2')
     I.see('Amazon Nevlad (Available)', 'table tr.row2')
     I.fillField('select[name="action"]', 'Mark Google account as Qualified')
     I.click('Go')
     I.fillField('select[name="action"]', 'Mark Amazon account as Qualified')
     // pause()
     I.see('Facebook olvida@mail.ru (Qualified)', 'table tr.row2')
     
    });
    
    
    Scenario('qualified', (I) => {
       I.amOnPage('http://localhost:8443/app/admin/')
       I.see('Adsrental Administration')
       I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
       I.fillField('input[name="password"]', 'team17')
       I.click('Log in')
       I.see('Dashboard')
       I.click('Raspberry pis')
       I.checkOption('input[type="checkbox"]')
       I.fillField('select[name="action"]', 'reset_cache')
       I.click('Go')


});

Scenario('bundlerDenerated', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Bundlers')
    I.fillField('input[name="q"]', 'Jason@clicktechmarketing.com')
    I.click('Go')
    I.see('Jason Taylor')
    I.see('600')
    I.see('1', 'table tr.row1 td.field-leads_count')
    I.click('a[href="/bundler/127/payments/"]')

});

Scenario('ping', async (I) =>{
    I.amOnPage('http://localhost:8443/log/?rpid=RP00001000&p=&version=2.0.8&attempt=1&hostname=123.123.123.123')
    I.see('result": true')
    I.see('"source": "ping"')
});

Scenario('check accounts status', async (I) =>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Leads')
    I.see('Google Neblad (In-Progress)', 'table tr.row2')
    I.see('Amazon Nevlad (Available)', 'table tr.row2')
    I.see('Facebook olvida@mail.ru (In-Progress)', 'table tr.row2')
    I.see('In-Progress', 'table tr.row2 td.field-status_field')


});

Scenario('check bundler payments', async (I) =>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Bundlers')
    I.fillField('input[name="q"]', '600')
    I.click('Search')
    I.see('Jason@clicktechmarketing.com')
    I.seeElement('td.field-is_active img[alt="True"]')
    I.click('Payments')
    I.waitForNavigation()
    I.see('Bundler Jason Taylor	')
    I.see('Total pay for Facebook accounts')
    I.see('Total pay for Google accounts')
    I.see('Total')
});

Scenario('check device log', async (I) =>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.waitForNavigation()
    I.see('Dashboard')
    I.click('Raspberry pis')
    I.waitForNavigation()
    I.see('Select raspberry pi to change')
    I.seeElement('td.field-online img[alt="True"]')
});

Scenario('timestamps', async (I) =>{
    I.amOnPage('http://localhost:8443/cron/lead_history/?now=true')
});

 Scenario('timestamps', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Lead Timestamps')
    I.see('Select Lead Timestamp to change')
    I.click('1732315')
    I.fillField('input[name="checks_online"]', '20')
    I.click('Save')
    I.click('Lead Timestamps') 
    I.seeElement('td.field-active img[alt="True"]')
    I.seeElement('td.field-online img[alt="True"]')
    // I.seeElement
    // pause()

    const titleSelector = 'table tr.row2 td.field-amount_field .has_note'
    I.seeInElementTitle('Facebook account in-progress', titleSelector)
    I.seeInElementTitle('Google account in-progress', titleSelector)
    I.seeInElementTitle('Amazon account is not in-progress', titleSelector)
    I.seeInElementTitle('Total: $0.9678', titleSelector)


});

Scenario('timestamps', async (I) =>{
   I.amOnPage('http://localhost:8443/cron/lead_history/?aggregate=true')

});

   Scenario('timestamps', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Lead Histories Month')
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

Scenario('googleBans', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Leads')
    I.see('Select lead to change')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban google account')
    I.click('Go')
    I.see('ban Google account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban amazon account')
    I.click('Go')
    I.see('ban Amazon account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban facebook account')
    I.click('Go')
    I.see('ban Facebook account')
    I.fillField('textarea[name="note"]', 'bad conection')
    I.click('Ban')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Ban lead')
    I.click('Go')
   
});
Scenario('googleBans', async (I) =>{
    I.loginAsAdmin()
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.fillField('input[name="q"]', '600')
    I.click('Search')
    I.click('Payments')
    
});