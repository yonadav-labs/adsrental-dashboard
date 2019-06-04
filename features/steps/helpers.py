from pathlib import Path
import time

import selenium
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium import webdriver
from django.conf import settings
from django.core.management import call_command

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.raspberry_pi import RaspberryPi

HOST = 'http://localhost:8000'


def start_webdriver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver


def login_as_admin(driver, username, password):
    driver.get(f"{HOST}/admin/login/")
    driver.find_element_by_name('username').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_css_selector('input[type=submit]').click()


@given('I am using initial database')
def use_test_database(_context):
    Lead.objects.all().delete()
    LeadAccount.objects.all().delete()
    RaspberryPi.objects.all().delete()
    call_command('loaddata', 'test.json')


@given('I am logged in as an Admin')
def logged_in_as_admin(context):
    context.driver = start_webdriver()
    login_as_admin(context.driver, "volshebnyi@gmail.com", "team17")


@given('I sign up as a lead')
def sign_up_as_lead(context):
    context.driver = start_webdriver()
    context.driver.get(f"{HOST}/?utm_source=600")
    context.driver.find_element_by_name('first_name').send_keys('Vlad')
    context.driver.find_element_by_name('last_name').send_keys('Emelianov')
    context.driver.find_element_by_name('email').send_keys('volshebnyii@gmail.com')
    context.driver.find_element_by_css_selector('#apply button').click()


@given('I am logged in as an Admin with wrong password')
def logged_in_as_admin_wrong_password(context):
    context.driver = webdriver.Chrome()
    login_as_admin(context.driver, "volshebnyi@gmail.com", "bvvgr")


@given('I am logged in as user')
def logged_in_as_user(context):
    context.driver = start_webdriver()
    context.driver.get(f"{HOST}/user/login/")
    context.driver.find_element_by_name('first_name').send_keys('Vlad')
    context.driver.find_element_by_name('last_name').send_keys('Emelianov')
    context.driver.find_element_by_name('postal_code').send_keys('6348489')
    context.driver.find_element_by_css_selector('button[type=submit]').click()


@when('I type "{text}" in field "{name}"')
def type_text(context, text, name):
    context.driver.find_element_by_name(name).send_keys(text)


@when('I upload file "{filepath}" in field "{name}"')
def upload_file(context, filepath, name):
    path = Path(settings.BASE_DIR) / 'features' / 'assets' / filepath
    context.driver.find_element_by_name(name).send_keys(path.as_posix())


@given('I am on main Admin Dashboard page')
def on_main_admin_page(context):
    context.driver.get(f"{HOST}/admin/")
    context.driver.page_source.find('Dashboard')


@then('I should see {state} check mark in column "{column_name}"')
def i_see_disabled_check(context, state, column_name):
    alt = 'true' if state == 'enabled' else 'false'
    column = context.driver.find_element_by_xpath(f'//th/div[@class="text"]/a[contains(text(), "{column_name}")]/../..')
    column_classes = column.get_attribute('class').split(' ')
    field_class = None
    for column_class in column_classes:
        if column_class.startswith('column-'):
            field_class = column_class.replace('column-', 'field-')
    check_mark = context.driver.find_element_by_css_selector(f'td.{field_class} img')
    context.test.assertEqual(check_mark.get_attribute('alt'), alt, 'Check mark has wrong state')



@when('I click link "{link_text}"')
def click_link(context, link_text):
    context.driver.find_element_by_link_text(link_text).click()


@when('I click button "{button_text}"')
def click_button(context, button_text):
    try:
        element = context.driver.find_element_by_xpath(f'//button[contains(text(), "{button_text}")]')
    except selenium.common.exceptions.NoSuchElementException:
        element = context.driver.find_element_by_css_selector(f'input[value="{button_text}"]')
    element.click()





@when('I click radio with name "{name}" and value "{value}"')
def click_radio_with_name(context, name, value):
    css_selector = f'input[type="radio"][name="{name}"][value="{value}"]'
    context.driver.find_element_by_css_selector(css_selector).click()


@when('I click checkbox with name "{name}"')
def click_checkbox_with_name(context, name):
    context.driver.find_element_by_name(name).click()

@then('I should see text on page "{text}"')
def when_see_text_on_page(context, text):
    context.test.assertTrue(text in context.driver.page_source, f'Text "{text}" not found on page')

@then('I should see "{title}" when i hover {selector}')
def seee_title(context, title, selector):
    element = context.driver.find_element_by_css_selector(selector)
    context.text.assertEqual(element.get_attribute('title'), title)


@then('I should see "{title}" page title')
def see_page_title(context, title):
    context.test.assertEqual(context.driver.title, title)


@then('I should see "{text}" in "{selector}"')
def see_page_title(context, text, selector):
    element = context.driver.find_element_by_css_selector(selector)
    context.test.assertTrue(text in element.text, f"Element has text {element.text}, expected {text}")


@then('I should see "{text}" in column "{column_name}"')
def see_page_title(context, text, column_name):
    column = context.driver.find_element_by_xpath(f'//th/div[@class="text"]/a[contains(text(), "{column_name}")]/../..')
    column_classes = column.get_attribute('class').split(' ')
    field_class = None
    for column_class in column_classes:
        if column_class.startswith('column-'):
            field_class = column_class.replace('column-', 'field-')

    element = context.driver.find_element_by_css_selector(f'td.{field_class}')
    context.test.assertTrue(text in element.text, f"Element has text {element.text}, expected {text}")


@then('I am on url "{url}"')
def i_am_on_url(context, url):
    context.test.assertEqual(context.driver.current_url, HOST + url)


@then('Admin Dashboard should be shown')
def admin_dashboard_should_be_shown(context):
    context.test.assertTrue('Adsrental Administration' in context.driver.page_source, 'It is not Admin Dashboard page')


@then('I wait')
def i_wait(context):
    time.sleep(1000)
