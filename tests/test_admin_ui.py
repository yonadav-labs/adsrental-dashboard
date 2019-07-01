import unittest
from selenium import webdriver
import time


class TestAdminUI(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='./e2e_tests/node_modules/chromedriver/bin/chromedriver')
        self.driver.get("http://localhost:8000/admin/login/")

    def tearDown(self):
        self.driver.quit()

    def test_admin_links(self):
        self.driver.find_element_by_name('username').send_keys("volshebnyi@gmail.com")
        self.driver.find_element_by_name('password').send_keys("team17")
        self.driver.find_element_by_css_selector('input[type=submit]').click()
        self.driver.page_source.find('Dashboard')
        self.driver.find_element_by_link_text('Leads').click()
        self.driver.find_element_by_link_text('Proxy tunnel').click()
        self.driver.page_source.find('RP999 proxy tunnel info')
        self.driver.find_element_by_link_text('Admin').click()
        self.driver.page_source.find('Dashboard')
        self.driver.find_element_by_link_text('Leads').click()
        self.driver.find_element_by_link_text('pi.conf').click()
        self.driver.find_element_by_link_text('Stats').click()
        self.driver.page_source.find('Leads')
        self.driver.find_element_by_link_text('Admin').click()
        self.driver.page_source.find('Dashboard')
        self.driver.find_element_by_link_text('Leads').click()
        self.driver.find_element_by_link_text('History').click()
        self.driver.page_source.find('Select lead change to change')
        self.driver.find_element_by_link_text('Home').click()
        self.driver.find_element_by_link_text('Leads').click()
        self.driver.find_element_by_link_text('Checks').click()
        self.driver.page_source.find('Select Lead History Month to change')
        self.driver.find_element_by_link_text('Home').click()
        self.driver.find_element_by_link_text('Leads').click()
        self.driver.find_element_by_link_text('Cost').click()
        self.driver.page_source.find('Monthly payments')
