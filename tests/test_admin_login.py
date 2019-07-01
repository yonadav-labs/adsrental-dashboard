import unittest
from selenium import webdriver


class TestAdminLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='./e2e_tests/node_modules/chromedriver/bin/chromedriver')
        self.driver.get("http://localhost:8000/admin/login/")

    def tearDown(self):
        self.driver.quit()

    def test_admin_login(self):
        self.driver.find_element_by_name('username').send_keys("volshebnyi@gmail.com")
        self.driver.find_element_by_name('password').send_keys("team17")
        self.driver.find_element_by_css_selector('input[type=submit]').click()
        self.driver.page_source.find('Adsrental Administration')

    def test_admin_login_failed(self):
        self.driver.find_element_by_name('username').send_keys("wrong@gmail.com")
        self.driver.find_element_by_name('password').send_keys("team17")
        self.driver.find_element_by_css_selector('input[type=submit]').click()
        self.driver.page_source.find('Please enter the correct email and password')
