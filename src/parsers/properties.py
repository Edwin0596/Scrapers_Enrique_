"""
This module contains functions to parse property pages from the website.
It includes functions to parse individual properties, as well as functions
to parse multiple properties from a search result page.
The module also includes helper functions to extract specific information
from the property page, such as the property ID, title, location, and price.
"""

import re
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src import property as P


def parse_by_xpath(driver: webdriver.Chrome, xpath: str) -> str:
    """
    Parses element by XPATH
    """
    element = driver.find_element(By.XPATH, xpath)
    return element.text.strip()


def parse_property(driver: webdriver.Chrome, url: str) -> P.Property:
    """
    Parses a single property page
    """

    if driver.current_url != url:
        driver.get(url)
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()

    pid = url.split("/")[-1]

    title = parse_by_xpath(
        driver, "//h1[@class='text-5xl font-bold text-[#212121] w-[500px]']"
    )

    location = (
        parse_by_xpath(
            driver,
            "//p[@class='text-xl font-normal text-[#757575]"
            + " mt-2 flex justify-start items-center gap-1']",
        )
        .split(" ", 1)[1]
        .strip()
    )

    estimated_completion_date = parse_by_xpath(
        driver, "//span[@class='font-bold']"
    )

    construction_company = parse_by_xpath(
        driver, "//h3[@class='text-xl font-semibold text-[#212121]']"
    )

    construction_status = parse_by_xpath(
        driver, "//li[@class='item-time active']//span[@class='text']"
    )

    nearby_places_elements = driver.find_elements(
        By.XPATH,
        "//div[@id='Sitios cercanos']//p[@class='text-[#757575] inline-block']",
    )
    nearby_places = [place.text.strip() for place in nearby_places_elements]

    amenities_elements = driver.find_elements(
        By.XPATH,
        "//div[@id='Amenidades']//p[@class='text-[#757575] inline-block']",
    )
    amenities = [amenity.text.strip() for amenity in amenities_elements]

    units = parse_units(driver, url)

    return P.Property(
        pid=pid,
        title=title,
        location=location,
        url=url,
        estimated_completion_date=estimated_completion_date,
        construction_company=construction_company,
        construction_status=construction_status,
        amenities=amenities,
        nearby_places=nearby_places,
        units=units,
    )


def parse_units(driver: webdriver.Chrome, url: str) -> list[P.Unit]:
    """
    Parses the units to get the unit details.
    """

    if driver.current_url != url:
        driver.get(url)
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()

    # Click choose unit btn
    driver.find_element(
        By.XPATH,
        "//button[contains(text(), 'Elegir unidad')]",
    ).click()

    # Wait until card groups are visible
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-group"))
    )

    units: list[P.Unit] = []
    card_groups = driver.find_elements(By.CSS_SELECTOR, "div.card-group")

    if not card_groups:
        print("No units found")
        return units

    for card_group in card_groups:
        # Find each unit within the card group
        unit_elements = card_group.find_elements(  # type: ignore
            By.CSS_SELECTOR, "div.label-option"
        )

        for unit_element in unit_elements:
            details = {
                "price": 0.0,
                "rooms": 0.0,
                "bathrooms": 0.0,
                "area_m2": 0.0,
                "area_v2": 0.0,
            }

            unit_name = unit_element.find_element(  # type: ignore
                By.CSS_SELECTOR, "h3.font-semibold.text-base"
            ).text.strip()

            # Extract and format price
            unit_price_text = unit_element.find_element(  # type: ignore
                By.CSS_SELECTOR, "p.text-base.font-normal.text-\\[\\#212121\\]"
            ).text.strip()

            price_match = re.search(r"[\d,]+(?:\.\d+)?", unit_price_text)
            if price_match:
                details["price"] = float(
                    price_match.group()
                    .replace(",", "")
                    .replace("$", "")
                    .strip()
                )
            else:
                details["price"] = 0.0  # Default value if no price found

            container = unit_element.find_elements(  # type: ignore
                By.CSS_SELECTOR,
                "div.flex.flex-wrap",
            )

            for element in container:
                texts = element.text.strip().lower().split("\n")

                for line in texts:
                    amount = float(line.split(" ")[0].replace(",", ""))

                    if "habitaciones" in line or "habitación" in line:
                        details["rooms"] = amount
                    if "baños" in line or "baño" in line:
                        details["bathrooms"] = amount
                    if "m2" in line:
                        details["area_m2"] = amount
                    if "v2" in line:
                        details["area_v2"] = amount

            units.append(
                P.Unit(
                    name=unit_name,
                    price=details["price"],
                    rooms=details["rooms"],
                    bathrooms=details["bathrooms"],
                    area_m2=details["area_m2"],
                    area_v2=details["area_v2"],
                )
            )

    return units
