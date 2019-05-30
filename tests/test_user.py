import unittest
from selenium import webdriver


class TestUser(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='./e2e_tests/node_modules/chromedriver/bin/chromedriver')
        self.driver.get("http://localhost:8000/user/login/")

    def tearDown(self):
        self.driver.quit()

    def test_user_timestamps(self):
        self.driver.find_element_by_name('first_name').send_keys("Vlad")
        self.driver.find_element_by_name('last_name').send_keys("Emelianov")
        self.driver.find_element_by_name('postal_code').send_keys("80636")
        self.driver.find_element_by_tag_name('button').click()
        self.driver.page_source.find('Lead volshebnyi@gmail.com stats')
        self.driver.page_source.find('Your Google account volshebnyi@gmail.com is In-Progress')
        self.driver.page_source.find('Your Facebook account volshebnyi_fb@gmail.com is In-Progress')
        self.driver.page_source.find('Your Amazon account volshebnyi_am@gmail.com is Available')
        self.driver.find_elements_by_link_text('Timestamps')[0].click()
        self.driver.page_source.find('daily stats for')
        self.driver.page_source.find('Aug. 31, 2018 - Online ($0.8065')
        self.driver.find_element_by_partial_link_text('Back to stats').click()
        self.driver.page_source.find('General info')
        self.driver.find_elements_by_link_text('Timestamps')[1].click()
        self.driver.page_source.find('daily stats for')
        self.driver.find_element_by_partial_link_text('Back to stats').click()
        self.driver.page_source.find('General info')
        self.driver.find_elements_by_link_text('Timestamps')[2].click()
        self.driver.page_source.find('daily stats for')
        self.driver.find_element_by_partial_link_text('Back to stats').click()
        self.driver.find_elements_by_link_text('Timestamps')[3].click()
        self.driver.page_source.find('General info')
       




# I.amOnPage('http://localhost:8000/user/login/')
# I.see('User sign in')
# I.fillField('input[name="first_name"]', 'Vlad')
# I.fillField('input[name="last_name"]', 'Emelianov')
# I.fillField('input[name="postal_code"]', '80636')
# I.click('Sign in')
# I.see('Lead volshebnyi@gmail.com stats')
# I.see('Your Google account volshebnyi@gmail.com is In-Progress')
# I.see('Your Facebook account volshebnyi_fb@gmail.com is In-Progress')
# I.see('Your Amazon account volshebnyi_am@gmail.com is Available')
# I.click('a[href="/user/stats/timestamps/?date=2018-08-01"]')
# I.see('daily stats for')
# I.see('Aug. 31, 2018 - Online ($0.8065)')
# I.click('Back to stats')
# I.see('General info')
# I.click('a[href="/user/stats/timestamps/?date=2018-04-01"]')
# I.see(' daily stats for')
# I.click('Back to stats')
# I.see('General info')
# I.click('a[href="/user/stats/timestamps/?date=2018-03-01"]')
# I.see('daily stats for')
# I.click('Back to stats')
# I.see('General info')
# I.click('a[href="/user/stats/timestamps/?date=2018-02-01"]')


# });
