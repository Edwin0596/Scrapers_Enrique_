"""
Driver setup for webparsing
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def setup_options(headless: bool = False) -> Options:
    """
    Configures the Chrome driver with the desired options
    """
    options = Options()

    if headless:
        options.add_argument("--headless")  # type: ignore # run Chrome in headless mode

    options.add_argument(  # type: ignore
        "--window-size=1920,1080"
    )  # set window size to native GUI size
    options.add_argument("start-maximized")  # type: ignore # ensure window is full-screen

    return options


def make_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Creates a Chrome driver with the desired options
    """
    options = setup_options(headless)
    driver = webdriver.Chrome(options=options)
    return driver


def get_page_source(
    driver: webdriver.Chrome,
    url: str,
    css_selector: str,
    timeout: int = 30,
) -> str:
    """
    Gets the page source of a given URL and waits for a specific CSS element to be present
    """
    driver.get(url)

    WebDriverWait(driver=driver, timeout=timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )

    return driver.page_source
