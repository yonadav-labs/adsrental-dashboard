const assert = require('assert');
const uuid = require('uuid/v4');

function getRandomDigits(length) {
    let result = '';
    for (let i=0; i < length ; i++) {
        result += Math.floor(Math.random() * 10)
    }
   return result;
}
   


Feature('My Adsrental Test');

// Scenario('test main page', (I) => {
//   I.amOnPage('http://localhost:8443/?utm_source=600');
//   I.see('EARN CASH NOW');
//   I.fillField('First name', 'asd');
//   I.wait(1000);
// });


// Scenario('test no last name', (I) => {
//     I.amOnPage('http://localhost:5000');
//     I.see('Hi there!');
//     I.fillField('First name', 'Vlad');
//     I.click('Continue');
//     I.see('Hi there');
// });
// Scenario('test botton', (I) => {
//     I.amOnPage('http://localhost:5000');
//     I.see('Hi there!');
//     I.fillField('First name', 'Vlad');
//     I.fillField('Last name', 'Emelianov');
//     I.pressKey('Enter');
//     I.see('Hi Vlad Emelianov!');
//   });
//   Scenario('not me', (I) => {
//     I.amOnPage('http://localhost:5000');
//     I.see('Hi there!');
//     I.fillField('First name', 'Vlad');
//     I.fillField('Last name', 'Emelianov');
//     I.click('Continue');
//     I.see('Hi Vlad Emelianov!');
//     I.see('This is not me')
//   });
//   Scenario('not me', (I) => {
//     I.amOnPage('http://localhost:5000');
//     I.see('Hi there!');
//     I.fillField('First name', 'Vlad');
//     I.fillField('Last name', 'Emelianov');
//     I.click('Continue');
//     I.see('Hi Vlad Emelianov!');
//     I.see('This is not me');
//     I.click('This is not me');
//     I.see('Hi there!')
//   });
Scenario('ads', async (I) => {
    const randomID = uuid().split('-')[0]; 

    I.amOnPage('http://localhost:8443/?utm_source=600');
    I.see('Sign Up for free.');
    I.fillField('First name', 'Vlad')
    I.fillField('Last name' , 'Emelianow');
    I.fillField('Email address', 'volshebnyi_' + randomID + '@gmail.com')
    I.click('APPLY');
    I.waitForElement('body', 5)
    I.see('START MAKING EASY MONEY WITH ')
    I.seeElement('input[name="first_name"][value="Vlad"]')
    I.seeElement('input[name="last_name"][value="Emelianow"]')
    I.seeElement('input[name="email"][value="volshebnyi_' + randomID + '@gmail.com"]')
    // const text = await I.grabTextFrom('input[name="first_name"]');
    // throw Error(text)


    // I.wait(100)
    // I.see('volshebnyi@gmail.com')
    I.fillField('phone', '1'+getRandomDigits(9))
    I.fillField('input[name="facebook_profile_url"]', 'https://www.facebook.com/' + randomID)
    I.fillField('input[name="fb_email"]', 'olvida_ '+ randomID + '@mail.ru')
    I.fillField('input[name="fb_secret"]', '65656565')
    I.fillField('input[name="fb_friends"]', '150')
    I.fillField('input[name="street"]', 'fufuguf')
    I.fillField('input[name="apartment"]', '67')
    I.fillField('input[name="city"]', 'sfmsk_' + randomID)
    I.fillField('select[name="state"]', 'Oregon')
    I.fillField('input[name="postal_code"]', '5348489')
    I.attachFile('input[name="photo_id"]', './file.png')
    I.attachFile('input[name="extra_photo_id"]', './file.png')
    I.click('input[name="apply_type"][value="splashtop"]')
    I.click('input[name=accept]')
    I.checkOption('input[name=age_check]')
    I.click('Click Here to Apply')
    I.fillField('input[name="splashtop_id"]', '64644')
    I.click('Submit')
    I.see('Our agent will contact you shortly.')
});