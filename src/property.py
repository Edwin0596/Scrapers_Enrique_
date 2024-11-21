"""
Module defining classes
"""

import sqlite3
import csv
from datetime import datetime
from dataclasses import dataclass
import os


@dataclass
class Unit:
    """
    Class representing a unit in a property
    """

    name: str
    price: float
    rooms: float
    bathrooms: float
    area_m2: float
    area_v2: float


class Property:
    """
    Class representing a property
    """

    def __init__(
        self,
        pid: str,
        title: str,
        location: str,
        url: str,
        estimated_completion_date: str,
        construction_company: str,
        construction_status: str,
        amenities: list[str],
        nearby_places: list[str],
        units: list[Unit],
        parsing_time: str = str(datetime.date(datetime.now())),
    ):
        self.pid = pid
        self.title = title
        self.location = location
        self.url = url
        self.estimated_completion_date = estimated_completion_date
        self.construction_company = construction_company
        self.construction_status = construction_status
        self.amenities = amenities
        self.nearby_places = nearby_places
        self.units = units
        self.parsing_time = parsing_time

    def save_as_sqlite(self, db_path: str):
        """
        Save the property and its units to an SQLite database.
        """
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS property (
            id TEXT PRIMARY KEY,
            title TEXT,
            location TEXT,
            url TEXT,
            estimated_completion_date TEXT,
            construction_company TEXT,
            construction_status TEXT,
            amenities TEXT,
            nearby_places TEXT,
            parsing_time TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS unit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id TEXT,
            name TEXT,
            price REAL,
            rooms REAL,
            bathrooms REAL,
            area_m2 REAL,
            area_v2 REAL,
            FOREIGN KEY(property_id) REFERENCES property(id)
        )
        """)

        # Insert property data
        cursor.execute(
            """
        INSERT OR REPLACE INTO property (
            id, title, location, url, estimated_completion_date,
            construction_company, construction_status, amenities,
            nearby_places, parsing_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (  # type: ignore
                self.pid,
                self.title,
                self.location,
                self.url,
                self.estimated_completion_date,
                self.construction_company,
                self.construction_status,
                ", ".join(self.amenities),
                ", ".join(self.nearby_places),
                self.parsing_time,
            ),
        )

        # Insert unit data
        for unit in self.units:
            cursor.execute(
                """
            INSERT INTO unit (
                property_id, name, price, rooms, bathrooms, area_m2, area_v2
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.pid,
                    unit.name,
                    unit.price,
                    unit.rooms,
                    unit.bathrooms,
                    unit.area_m2,
                    unit.area_v2,
                ),
            )

        # Commit changes and close the connection
        conn.commit()
        conn.close()

    def save_as_csv(self, csv_path: str):
        """
        Save the property and its units to a CSV file.
        """
        property_headers = [
            "Property ID",
            "Title",
            "Location",
            "URL",
            "Estimated Completion Date",
            "Construction Company",
            "Construction Status",
            "Amenities",
            "Nearby Places",
            "Parsing Time",
        ]

        units_headers = [
            "Property ID",
            "Unit Name",
            "Price",
            "Rooms",
            "Bathrooms",
            "Area (m²)",
            "Area (v²)",
        ]

        if not os.path.exists(csv_path + "_properties.csv"):
            with open(
                csv_path + "_properties.csv",
                mode="w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(property_headers)
        else:
            with open(
                csv_path + "_properties.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(
                    [
                        self.pid,
                        self.title,
                        self.location,
                        self.url,
                        self.estimated_completion_date,
                        self.construction_company,
                        self.construction_status,
                        ", ".join(self.amenities),
                        ", ".join(self.nearby_places),
                        self.parsing_time,
                    ]
                )

        if not os.path.exists(csv_path + "_units.csv"):
            with open(
                csv_path + "_units.csv",
                mode="w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(units_headers)
        else:
            with open(
                csv_path + "_units.csv",
                mode="a",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.writer(csv_file)
                for unit in self.units:
                    writer.writerow(
                        [
                            self.pid,
                            unit.name,
                            unit.price,
                            unit.rooms,
                            unit.bathrooms,
                            unit.area_m2,
                            unit.area_v2,
                        ]
                    )
