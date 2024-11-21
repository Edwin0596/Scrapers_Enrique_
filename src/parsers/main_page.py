from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from parsel import Selector

from src.parsers import properties
from src import driver as Driver
from src import property as P


def parse_page(driver: webdriver.Chrome, url: str) -> list[P.Property]:
    """
    Returns the cards from the main page
    """
    # Main page, we extract all property links
    cards_css = "div.w-full.mb-5.mt-5.px-4.lg\\:px-0"
    page = Driver.get_page_source(
        driver,
        url,
        css_selector=cards_css,
        timeout=10,
    )

    selector = Selector(text=page)
    property_cards = selector.css(cards_css)
    props: list[P.Property] = []

    for card in property_cards:
        # Extract details from each card
        title = card.xpath(
            ".//h2[contains(@class, 'hidden lg:block')]/text()"
        ).get()
    
        try:
            if title:
                prop = parse_cards(driver, url, title)
                props.append(prop)
                print(f'Property "{prop.title}" parsed successfully.')
        except Exception as e:
            print(f'Unable to parse unit "{prop.title}": {e}')
            continue


    return props


def parse_cards(driver: webdriver.Chrome, url: str, title: str) -> P.Property:
    """
    Parses the cards to get the property details.
    """
    # Navigate to the URL if not already there
    if driver.current_url != url:
        driver.get(url)
        # Close any additional tabs except the main one
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()

    # Wait for the element to be clickable and click it
    wait = WebDriverWait(driver, 10)
    title_element = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//h2[contains(@class, 'hidden lg:block') and contains(text(), '{title}')]",
            )
        )
    )

    title_element.click()

    # Wait for the new tab to open and switch to it
    wait.until(EC.number_of_windows_to_be(2))
    property_window = driver.window_handles[-1]
    driver.switch_to.window(property_window)

    # Wait for the page to load
    try:
        print(f"- Trying to parse {driver.current_url}")
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//h1[contains(@class, 'text-5xl font-bold text-[#212121] w-[500px]') and contains(text(), '{title}')]",
                )
            )
        )
        
        prop = properties.parse_property(driver=driver, url=driver.current_url)
        print(f"+ Parsed {prop.title} succesfully")
    except:
        print(f"- Unable to parse property {driver.current_url}")
        return
    finally:
        # Close the current tab and switch back to the main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return prop
