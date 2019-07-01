// in this file you can append custom step methods to 'I' object

module.exports = function () {
  return actor({
    seeChecked: function (selector) {
      this.seeElement(selector + ' span.glyphicon-ok')
    },
    seeUnchecked: function (selector) {
      this.seeElement(selector + ' span.glyphicon-remove')
    },
    loginAsAdmin: function () {
      this.amOnPage('http://localhost:8443/admin/login/')
      this.see('Adsrental Administration')
      this.fillField('input[name="username"]', 'volshebnyi@gmail.com')
      this.fillField('input[name="password"]', 'team17')
      this.click('Log in')
    },
    seeInElementTitle: function (text, selector) {
      this.seeElement(selector + '[title*="' + text + '"]')
    },
    amOnAdsrentalPage: function(url){
      this.amOnPage('http://localhost:8443' + url)
    }
  });
}