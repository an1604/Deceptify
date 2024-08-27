import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.support.wait import WebDriverWait

import os

load_dotenv()

base_url = 'http://localhost:5000/'

username = os.getenv('TEST_USERNAME')
email = os.getenv('TEST_EMAIL')
password = os.getenv('TEST_PASSWORD')


def test_register_user(passed=None):
    global base_url, username, email, password
    try:
        driver = webdriver.Chrome()
        driver.get(f'{base_url}auth/register')

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'username')))
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'email')))
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'password')))

        driver.find_element(By.ID, 'username').send_keys(username)
        driver.find_element(By.ID, 'email').send_keys(email)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.ID, 'submit').click()

        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))
    except Exception as e:
        if passed is not None:
            passed = False


def test_login_user(passed=None):
    global base_url, email
    try:
        driver = webdriver.Chrome()
        driver.get(f'{base_url}auth/login')

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'email')))
        driver.find_element(By.ID, 'email').send_keys(email)
        driver.find_element(By.ID, 'submit').click()

        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))
    except Exception as e:
        if passed is not None:
            passed = False
