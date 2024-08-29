from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:5000"
TEST_USERNAME = os.getenv('TEST_USERNAME')
TEST_EMAIL = os.getenv('TEST_EMAIL')
TEST_PASSWORD = os.getenv('TEST_PASSWORD')
ZOOM_DEFAULT_EMAIL = os.getenv("ZOOM_DEFAULT_EMAIL")
ZOOM_DEFAULT_PASSWORD = os.getenv("ZOOM_DEFAULT_PASSWORD")

ZOOM_SUBMIT_BTN = """//*[@id="zoom-auth"]/div/div[5]/div/div[4]/div[1]/button"""


def login(driver=None):
    logging.info("Logging in...")

    try:
        if driver is None:
            driver = webdriver.Chrome()
        driver.get(f'{BASE_URL}/auth/login')

        logging.info("Got the login page")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        logging.info("Found the email element")

        email_input = driver.find_element(By.ID, 'email')
        email_input.clear()
        logging.info("Cleared the email element")

        email_input.send_keys(TEST_EMAIL)

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element(By.ID, 'submit').click()
        logging.info("Submitting the login page")

        WebDriverWait(driver, 5).until(EC.url_contains(BASE_URL))
        logging.info("Found the base utl")

        return driver
    except Exception as e:
        print(f'Cannot login because this error occurred: {e}')
        if driver:
            driver.quit()
        return None


def automate_attack_generation():
    logging.basicConfig(level=logging.INFO)
    driver = None

    try:
        driver = login()
        if driver is None:
            logging.error("Login failed, cannot proceed with attack generation.")
            return

        logging.info("Driver initialized and logged in successfully.")

        driver.get(f'{BASE_URL}/new_ai_attack')
        print("Scrolling in line 65")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Done Scrolling")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'submit')))
        logging.info("Navigated to new AI attack page.")
        driver.find_element(By.ID, 'submit').click()

        # Wait for the Zoom sign-in page
        WebDriverWait(driver, 5).until(EC.url_contains('https://zoom.us/signin?'))
        logging.info("Zoom sign-in page loaded.")

        # Handle the Zoom login page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        driver.find_element(By.ID, 'email').send_keys(ZOOM_DEFAULT_EMAIL)
        driver.find_element(By.ID, 'password').send_keys(ZOOM_DEFAULT_PASSWORD)

        driver.find_element(By.ID, 'js_btn_login').click()
        logging.info("Zoom credentials entered and login button clicked.")

        # Handle the Zoom acceptation page
        WebDriverWait(driver, 5).until(EC.url_contains('https://marketplace.zoom.us/'))
        print("Scrolling in line 86")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Done Scrolling")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ZOOM_SUBMIT_BTN)))
        driver.find_element(By.XPATH, ZOOM_SUBMIT_BTN).click()
        logging.info("Zoom marketplace page loaded and submit button clicked.")

        # Wait for the next page and submit the form
        WebDriverWait(driver, 10).until(EC.url_contains(f"{BASE_URL}/generate_zoom_record"))
        print("Scrolling in line 95")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Done Scrolling")
        driver.find_element(By.ID, 'submit').click()
        logging.info("Submitted form on generate Zoom record page.")

        # Wait until the transition to the attack dashboard
        WebDriverWait(driver, 10).until(EC.url_contains(f"{BASE_URL}/attack_dashboard_transition"))
        logging.info("Transitioned to attack dashboard.")

        # Attempt to click the attack button
        clicked = False
        max_retries = 5
        retries = 0

        while not clicked and retries < max_retries:
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'attackBtn')))
                driver.find_element(By.ID, 'attackBtn').click()
                clicked = True
                logging.info("Attack button clicked successfully.")
            except (NoSuchElementException, TimeoutException) as e:
                logging.warning(f"Retrying click on attack button due to error: {e}")
                retries += 1
            except WebDriverException as e:
                logging.error(f"WebDriverException encountered: {e}")
                break  # Exit loop on a critical WebDriver error

        if not clicked:
            logging.error("Failed to click the attack button after multiple attempts.")

    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Encountered an error during automation: {e}")
    except WebDriverException as e:
        logging.error(f"WebDriver exception: {e}")
    finally:
        # Ensure the driver is closed properly
        if driver is not None:  # Check if the driver is initialized
            driver.quit()
            logging.info("Driver closed successfully.")


automate_attack_generation()
