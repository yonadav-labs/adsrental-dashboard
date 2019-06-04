
from selenium import webdriver


def before_scenario(context, _scenario):
    driver = webdriver.Chrome()
    driver.maximize_window()
    context.driver = driver
    context.host = 'http://localhost:8000'


def after_scenario(context, _scenario):
    context.driver.close()
