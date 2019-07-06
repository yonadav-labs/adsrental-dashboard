from pathlib import Path
import time

import selenium
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium import webdriver
from django.conf import settings
from django.core.management import call_command

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_history import LeadHistory
from adsrental.models.raspberry_pi import RaspberryPi


def login_as_admin(context, username, password):
    context.driver.get(f"{context.host}/admin/login/")
    context.driver.find_element_by_name('username').send_keys(username)
    context.driver.find_element_by_name('password').send_keys(password)
    context.driver.find_element_by_css_selector('input[type=submit]').click()


@given('I am using initial database')
def use_test_database(_context):
    Lead.objects.all().delete()
    LeadAccount.objects.all().delete()
    LeadHistory.objects.all().delete()
    RaspberryPi.objects.all().delete()
    call_command('loaddata', 'test.json')


@given('I am logged in as an Admin')
def logged_in_as_admin(context):
    login_as_admin(context, "volshebnyi@gmail.com", "team17")


@given('I go to url "{url}"')
def go_to_url(context, url):
    context.driver.get(f"{context.host}{url}")


@given('I sign up as a lead')
def sign_up_as_lead(context):
    context.driver.get(f"{context.host}/?utm_source=600")
    context.driver.find_element_by_name('first_name').send_keys('Vlad')
    context.driver.find_element_by_name('last_name').send_keys('Emelianov')
    context.driver.find_element_by_name('email').send_keys('volshebnyii@gmail.com')
    context.driver.find_element_by_css_selector('#apply button').click()


@given('I am logged in as an Admin with wrong password')
def logged_in_as_admin_wrong_password(context):
    login_as_admin(context, "volshebnyi@gmail.com", "bvvgr")


@given('I am logged in as user')
def logged_in_as_user(context):
    context.driver.get(f"{context.host}/user/login/")
    context.driver.find_element_by_name('first_name').send_keys('Vlad')
    context.driver.find_element_by_name('last_name').send_keys('Emelianov')
    context.driver.find_element_by_name('postal_code').send_keys('6348489')
    context.driver.find_element_by_css_selector('button[type=submit]').click()


@when('I type "{text}" in field "{name}"')
def type_text(context, text, name):
    element = context.driver.find_element_by_name(name)
    if element.tag_name != 'select':
        element.clear()
    element.send_keys(text)


@when('I upload file "{filepath}" in field "{name}"')
def upload_file(context, filepath, name):
    path = Path(settings.BASE_DIR) / 'features' / 'assets' / filepath
    text = path.as_posix()
    element = context.driver.find_element_by_name(name)
    element.clear()
    element.send_keys(text)


@given('I am on main Admin Dashboard page')
def on_main_admin_page(context):
    context.driver.get(f"{context.host}/admin/")
    context.driver.page_source.find('Dashboard')


@given('I am on user login page')
def on_user_login_page(context):
    context.driver.get(f"{context.host}/user/login/")


@then('I should see {state} check mark in column "{column_name}"')
def i_see_disabled_check(context, state, column_name):
    alt = 'true' if state == 'enabled' else 'false'
    column = context.driver.find_element_by_xpath(f'//th/div[@class="text"]/*[contains(text(), "{column_name}")]/../..')
    column_classes = column.get_attribute('class').split(' ')
    field_class = None
    for column_class in column_classes:
        if column_class.startswith('column-'):
            field_class = column_class.replace('column-', 'field-')
    check_mark = context.driver.find_element_by_css_selector(f'td.{field_class} img')
    context.test.assertEqual(check_mark.get_attribute('alt').lower(), alt, 'Check mark has wrong state')


@when('I click link "{link_text}"')
def click_link(context, link_text):
    context.driver.find_element_by_link_text(link_text).click()


@when('I click the first row in table')
def click_first_row(context):
    context.driver.find_element_by_css_selector('tr.row1 .field-id a').click()


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
    max_seconds = 3
    for i in range(max_seconds):
        page_text = context.driver.page_source
        if text in page_text:
            return
        time.sleep(1)

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
def I_should_see_in_column(context, text, column_name):
    column = context.driver.find_element_by_xpath(f'//th/div[@class="text"]/*[contains(text(), "{column_name}")]/../..')
    column_classes = column.get_attribute('class').split(' ')
    field_class = None
    for column_class in column_classes:
        if column_class.startswith('column-'):
            field_class = column_class.replace('column-', 'field-')

    element = context.driver.find_element_by_css_selector(f'td.{field_class}')
    context.test.assertTrue(text in element.text, f"Element has text {element.text}, expected {text}")


# @then('I should see "{text}" in column "{coulmn_name}" where row contains "{row_text}"')
# def i_see_


@then('I am on url "{url}"')
def i_am_on_url(context, url):
    context.test.assertEqual(context.driver.current_url, context.host + url)


@then('Admin Dashboard should be shown')
def admin_dashboard_should_be_shown(context):
    context.test.assertTrue('Adsrental Administration' in context.driver.page_source, 'It is not Admin Dashboard page')


@when('I wait')
def i_wait(context):
    time.sleep(1000)


@when('I wait {seconds} seconds')
def i_wait(context, seconds):
    time.sleep(int(seconds))


@then('I see hint "{text}"')
def i_see_hint(context, text):
    element = context.driver.find_element_by_class_name('has_note')
    title = element.get_attribute('title')
    context.test.assertTrue(text in title, f'No hint found with text "{text}"')
