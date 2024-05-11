import os
import pytest
from re import match
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException


TESTING_URL = os.getenv("TESTING_URL", "http://localhost:8091/")
MIN_POSITION = -19


@pytest.fixture
def browser():
    # Use CHROME_PATH if set, otherwise use the default path.
    options = Options()
    chrome_path = os.getenv("CHROME_PATH")
    if chrome_path is not None:
        options.binary_location = chrome_path
    driver = webdriver.Chrome(options=options)
    # Delete all cookies, so that there would be a clean session every time.
    driver.delete_all_cookies()
    yield driver
    driver.quit()


@pytest.mark.parametrize("left_clicks", [20, 21, 25, 100])
def test_unrestricted_left_movement(browser: webdriver.Chrome, left_clicks: int):
    browser.get(TESTING_URL)
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, "login-btn"))).click()

    # Try to spam the left arrow button to move past the boundary.
    for _ in range(left_clicks):
        # Clicking the left arrow button may produce a stale element reference exception,
        # so we catch it and try again in a while loop.
        while True:
            try:
                WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, "arrowLeft"))).click()
                break
            except StaleElementReferenceException:
                pass

    # Wait till we have moved.
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation.hidden")))
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation")))

    # Extract the place value.
    place_element = browser.find_element(By.ID, "place")
    matched_text = match(r".*\[(.+)\]", place_element.text)
    assert matched_text is not None
    got_place = int(matched_text.group(1))
    
    # Place should be MIN_POSITION, since we can't move past it.
    assert got_place == MIN_POSITION
