

Feature('Lead Lifespan Test');

Scenario('signup', async (I) => {
    I.amOnPage('http://localhost:8443/?utm_source=600');
    I.see('Sign Up for free.');
    I.fillField('First name', 'Blad')
    I.fillField('Last name', 'Newone');
    I.fillField('Email address', 'volshebnyii@gmail.com')
    I.click('APPLY');
    I.waitForElement('body', 5)
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
    I.see('Select lead to change')
    I.checkOption('table tr.row2 td.action-checkbox input')
    I.fillField('select[name="action"]', 'Mark Facebook account as qualified')
    I.click('Go')
    I.see('Qualified', 'table tr.row2 td.field-status_field')
    I.click('RP00001000')
    I.checkOption('input[name="_selected_action"]')
    I.click('RP00001000')
    I.see('Change raspberry pi')
    I.click('.field-first_tested .datetimeshortcuts:nth-of-type(1) a:nth-of-type(1)')
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