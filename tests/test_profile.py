import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv

import os

load_dotenv()

base_url = 'http://localhost:5000/'

username = os.getenv('TEST_USERNAME')
email = os.getenv('TEST_EMAIL')
password = os.getenv('TEST_PASSWORD')


def login(driver):
    try:
        driver.get(f'{base_url}auth/login')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        driver.find_element(By.ID, 'email').send_keys(email)
        driver.find_element(By.ID, 'submit').click()

        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))

        # Step 2: Click on the "Create Profile" button
        create_profile_btn_xpath = '/html/body/div[2]/div[3]/a[3]'
        create_profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, create_profile_btn_xpath))
        )
        create_profile_button.click()

        # Ensure the navigation to the new profile creation page
        WebDriverWait(driver, 10).until(EC.url_contains('new_profile'))
        return driver
    except Exception as e:
        print(f'Cannot login because this error occur: {e}')


@pytest.fixture
def driver():
    # Setup WebDriver
    driver = webdriver.Chrome()
    yield driver
    # Teardown WebDriver
    driver.quit()


def test_create_profile(driver):
    try:
        # Step 1: Log in as the test user
        login(driver)
        # Step 3: Fill in the profile creation form
        profile_name = "test_profile"
        general_info = "It's just a test"

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'name_field')))
        driver.find_element(By.ID, 'name_field').send_keys(profile_name)
        driver.find_element(By.ID, 'gen_info_field').send_keys(general_info)

        # Upload the voice file
        test_audio_filepath = os.path.join(os.getcwd(), 'files', 'test.mp3')
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        driver.execute_script("arguments[0].scrollIntoView(true);", file_input)
        file_input.send_keys(test_audio_filepath)

        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))

        assert driver.current_url == base_url, "Profile creation failed or did not redirect to the expected URL."

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e


def test_create_ai_attack(driver):
    try:
        login(driver)
        driver.get(f"{base_url}new_ai_attack")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
        driver.find_element(By.ID, "submit").click()

        WebDriverWait(driver, 5).until(EC.url_contains('https://zoom.us/signin?'))
        assert 'https://zoom.us/signin?' in driver.current_url
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
