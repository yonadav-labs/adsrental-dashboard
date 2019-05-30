from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium import webdriver
from behave_django.decorators import fixtures

HOST = 'http://localhost:8000'


def login_as_admin(driver, username, password):
    driver.get(f"{HOST}/admin/login/")
    driver.find_element_by_name('username').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_css_selector('input[type=submit]').click()


@fixtures('test.json')
@given('I am using initial database')
def use_test_database(_context):
    pass


@given('I am logged in as an Admin')
def logged_in_as_admin(context):
    context.driver = webdriver.Chrome()
    context.driver.maximize_window()
    login_as_admin(context.driver, "volshebnyi@gmail.com", "team17")


@given('I am logged in as user')
def logged_in_as_user(context):
    context.driver = webdriver.Chrome()
    context.driver.maximize_window()
    context.driver.get(f"{HOST}/user/login/")
    context.driver.find_element_by_name('first_name').send_keys('Vlad')
    context.driver.find_element_by_name('last_name').send_keys('Emelianov')
    context.driver.find_element_by_name('postal_code').send_keys('6348489')
    context.driver.find_element_by_css_selector('input[type=submit]').click()


@given('I am on main Admin Dashboard page')
def on_main_admin_page(context):
    context.driver.get(f"{HOST}/admin/")
    context.driver.page_source.find('Dashboard')


@when('I click link "{link_text}"')
def click_link(context, link_text):
    context.driver.find_element_by_link_text(link_text).click()


@then('I should see text on page "{text}"')
def see_test_on_page(context, text):
    context.test.assertTrue(text in context.driver.page_source, f'Text "{text}" not found on page')


@then('I should see "{text}" page title')
def see_page_title(context, title):
    context.test.assertEqual(context.driver.title, title)
