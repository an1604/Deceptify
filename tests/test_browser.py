import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def test_browser_type_and_version():
    driver = webdriver.Chrome()
    driver.get("about:blank")
    caps = driver.capabilities
    assert caps['browserName'] == 'chrome'
    print(caps['browserVersion'])
    driver.quit()


def test_cookies_management():
    driver = webdriver.Chrome()
    driver.get(f'http://localhost:5000/')

    # Checking the default cookies' capacity.
    cookies = driver.get_cookies()
    assert len(cookies) == 0

    # Adding another cookie, and then checks the capacity again.
    driver.add_cookie({'name': 'username', 'value': 'Gal'})
    cookies = driver.get_cookies()
    assert len(cookies) == 1
    driver.quit()
