"""
Main file for the web-scrapper program
"""

import sys
import os

# Add the 'src' directory to the Python path
# For imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import driver as Driver
import parsers.main_page as main_page


def main():
    """
    Entry point of the program
    """
    path = r"C:\Users\TDW\OneDrive - Inversiones Bolivar S.A de C.V\scrapers\propi_en_planos\db"
    print(f"Saving csv to path: {path}")

    driver = Driver.make_driver(headless=True)
    url = "https://www.propilatam.com/sv/venta/casas-y-apartamentos/proyectos"
    properties = main_page.parse_page(driver, url)
    print(f"Found {properties=}")

    for prop in properties:
        try:
            prop.save_as_csv(path)
            print(f'Saved "{prop.title}" to DB')
        except Exception as e:
            print(f"Unable to save {prop.title}: {e}")


if __name__ == "__main__":
    main()
