# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from typing import Dict
from dataclasses import dataclass
from timezonefinder import TimezoneFinder
from bs4 import BeautifulSoup

from utils.storage import Storage
from utils.uuid_ import generate_uuid

from .base import Scraped, Stored, ExpiredVersionError
from .country import Country, UnsupportedCountryError


@dataclass
class Event(Scraped, Stored):

    uuid: str
    name: str
    country: str
    latitude: float
    longitude: float
    start: str
    start_dst: str
    timezone: str
    mid: str

    version: str = "1.0.1"

    @staticmethod
    def directory() -> str: return "events"

    def generate_state(self) -> str: return generate_uuid(data=str(self.__dict__))

    @classmethod
    def refresh(cls, storage: Storage, data: Dict[str, any]) -> "Event":

        uuid = Event.extract_uuid(data=data)

        event_soup = cls.soup(url=data["url"])
        course_soup = cls.soup(url=os.path.join(data["url"], "course"))

        event = Event(
            uuid=uuid,
            name=data["properties"]["EventShortName"],
            country=Event.extract_country(data=data).display(),
            latitude=data["geometry"]["coordinates"][1],
            longitude=data["geometry"]["coordinates"][0],
            start=Event.extract_start(soup=event_soup, uuid=uuid, dst=False),
            start_dst=Event.extract_start(soup=event_soup, uuid=uuid, dst=True),
            timezone=TimezoneFinder().timezone_at(lng=data["geometry"]["coordinates"][0], lat=data["geometry"]["coordinates"][1]),
            mid=Event.extract_mid(soup=course_soup)
        )

        event.write(storage=storage, uuid=uuid)

        print(f"Refreshed for event: {event.name} | {event.country}")

        return event

    @classmethod
    def get(cls, storage: Storage, data: Dict[str, any]) -> "Event":

        uuid = Event.extract_uuid(data=data)

        try:
            raw = super().get(storage=storage, uuid=uuid)

            if raw.get("version") != Event.version: raise ExpiredVersionError()

            for key in ["state", "refreshed"]:
                if key in raw: del raw[key]

        except FileNotFoundError:
            event = Event.refresh(storage=storage, data=data)

        except ExpiredVersionError:
            event = getattr(cls, f"migrate_v{Event.version.replace('.', '_')}")(raw=raw)
            event.write(storage=storage, uuid=uuid)

        else:
            event = Event(**raw)

        return event

    @staticmethod
    def extract_country(data: Dict[str, any]) -> Country:

        try:
            return Country(data["properties"]["countrycode"])
        except ValueError as e:
            raise UnsupportedCountryError(data["properties"]["countrycode"]) from e

    @staticmethod
    def extract_uuid(data: Dict[str, any]) -> str:

        country = Event.extract_country(data=data)

        return generate_uuid(data=f"{country.value}|{data['id']}")

    @staticmethod
    def extract_start(soup: BeautifulSoup, uuid: str, dst: bool) -> str:

        content = soup.select_one("div#main div.homeleft")

        index = [h.text.strip() for h in content.select("h4")].index("When is it?")
        text = [p.text.strip() for p in content.select("p.paddetandb")][index]

        try:

            if re.search(r"daylight|saving|summer|winter", text) is None:

                time = re.search(r"(\d{1,2}):(\d{2})", text)

                if time is not None:
                    return f"{int(time.group(1)):02d}:{time.group(2)}"

                time = re.search(r"(\d{1,2})am", text)

                if time is not None:
                    return f"{int(time.group(1)):02d}:00"

                raise Exception(f"Unable to find start time from text: {text}")

            elif dst:
                time = re.search(r"(\d{1,2})am during daylight saving", text)
                return f"{int(time.group(1)):02d}:00"

            else:
                time = re.search(r"(\d{1,2})am during standard time", text)
                return f"{int(time.group(1)):02d}:00"

        except Exception as e:  # pylint: disable=W0703

            if uuid == "f4462738-1eb6-5094-9d2c-348beb1177c8":  # The Venue
                if dst:
                    return "07:00"
                else:
                    return "08:00"

            else:
                raise e

    @staticmethod
    def extract_mid(soup: BeautifulSoup) -> str:

        params = dict([tuple(p.split("=")) for p in soup.select_one("iframe").attrs["src"].split("?")[1].split("&")])

        return params["mid"]

    @staticmethod
    def migrate_v1_0_0(raw: Dict[str, any]) -> "Event":

        return Event(**{k: v for (k, v) in raw.items() if k in ["uuid", "name", "country", "latitude", "longitude", "start", "timezone", "mid"]})

    @staticmethod
    def migrate_v1_0_1(raw: Dict[str, any]) -> "Event":

        raw["start_dst"] = raw["start"]

        return Event(**{k: v for (k, v) in raw.items() if k in ["uuid", "name", "country", "latitude", "longitude", "start", "start_dst", "timezone", "mid"]})
