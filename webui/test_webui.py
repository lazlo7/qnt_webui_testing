from math import exp
import os
from time import time
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
MIN_TIME_TO_MOVE = 2


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


def extract_place_value(browser: webdriver.Chrome) -> int:
    place_element = browser.find_element(By.ID, "place")
    matched_text = match(r".*\[(.+)\]", place_element.text)
    assert matched_text is not None
    return int(matched_text.group(1))


@pytest.mark.parametrize("left_clicks", [20, 21, 25, 100])
def test_moving_past_left_boundary(browser: webdriver.Chrome, left_clicks: int):
    browser.get(TESTING_URL)
    WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, "login-btn"))).click()

    # Try to spam the left arrow button to move past the boundary.
    for _ in range(left_clicks):
        # Clicking the left arrow button may produce a stale element reference exception,
        # so we catch it and try again in a while loop.
        while True:
            try:
                WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, "arrowLeft"))).click()
                break
            except StaleElementReferenceException:
                pass

    # Wait till we have moved.
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation.hidden")))
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation")))
    
    # Place should be MIN_POSITION, since we can't move past it.
    assert extract_place_value(browser) == MIN_POSITION


@pytest.mark.parametrize("direction", ["left", "right"])
@pytest.mark.parametrize("clicks", [2, 3])
def test_moving_during_timer(browser: webdriver.Chrome, direction: str, clicks: int):
    browser.get(TESTING_URL)
    WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, "login-btn"))).click()

    arrow_id = "arrowLeft" if direction == "left" else "arrowRight"

    # Click the button many times.
    # We are aiming to move more than one place in less than 2 seconds.
    # Checking that the button could be clicked is not enough,
    # since the onClick() function may handle the click differently, depending on timer.
    for _ in range(clicks):
        while True:
            try:
                WebDriverWait(browser, 1).until(EC.element_to_be_clickable((By.ID, arrow_id))).click()
                break
            except StaleElementReferenceException:
                pass

    # Wait till we have moved.
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation.hidden")))
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.moveAnimation")))
    
    # If we managed to move on more than one place in less than 2 seconds, then that's a bug.
    expected_place = -1 if direction == "left" else 1
    assert extract_place_value(browser) == expected_place
