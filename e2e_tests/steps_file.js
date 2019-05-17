// in this file you can append custom step methods to 'I' object

module.exports = function () {
  return actor({

    // Define custom steps here, use 'this' to access default methods of I.
    // It is recommended to place a general 'login' function here.

    loginAsAdmin: function () {
      this.see('Adsrental Administration')
      this.fillField('input[name="username"]', 'volshebnyi@gmail.com')
      this.fillField('input[name="password"]', 'team17')
      this.click('Log in')
    },
  });
}