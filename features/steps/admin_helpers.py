from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium import webdriver


@given('I am logged in as an Admin')
def ligged_in_as_admin(context):
    driver = webdriver.Chrome(executable_path='./e2e_tests/node_modules/chromedriver/bin/chromedriver')
    context.driver = driver
    driver.get("http://localhost:8000/admin/login/")
    driver.find_element_by_name('username').send_keys("volshebnyi@gmail.com")
    driver.find_element_by_name('password').send_keys("team17")
    driver.find_element_by_css_selector('input[type=submit]').click()


@given('I am on main Admin Dashboard page')
def on_main_admin_page(context):
    context.driver.get("http://localhost:8000/admin/")
    context.driver.page_source.find('Dashboard')


@when('I click link "{link_text}"')
def click_link(context, link_text):
    context.driver.find_element_by_link_text(link_text).click()


@then('I should see text on page "{text}"')
def see_test_on_page(context, text):
    result = context.driver.page_source.find(text)
    context.test.assertTrue(result >= 0, f'Text "{text}" not found on page')
