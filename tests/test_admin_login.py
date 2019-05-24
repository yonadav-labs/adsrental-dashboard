import unittest
from selenium import webdriver


class TestAdminLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_admin_login(self):
        self.driver.get("http://localhost:8000/admin/login/")
        self.driver.find_element_by_name('username').send_keys("volshebnyi@gmail.com")
        self.driver.find_element_by_name('password').send_keys("team17")
        self.driver.find_element_by_css_selector('input[type=submit]').click()
        self.driver.page_source.find('Adsrental Administration')

    def test_admin_login_failed(self):
        self.driver.get("http://localhost:8000/admin/login/")
        self.driver.find_element_by_name('username').send_keys("wrong@gmail.com")
        self.driver.find_element_by_name('password').send_keys("team17")
        self.driver.find_element_by_css_selector('input[type=submit]').click()
        self.driver.page_source.find('Please enter the correct email and password')

    def tearDown(self):
        self.driver.quit()
