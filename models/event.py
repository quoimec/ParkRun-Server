# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from typing import Dict
from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_URL as uuid_namespace

from bs4 import BeautifulSoup
from utils.storage import Storage

from .base import Scraped, Stored
from .coordinate import Coordinate
from .map import Map
from .country import Country, UnsupportedCountryError


@dataclass
class Event(Scraped, Stored):

    uuid: str
    country: str
    name: str
    area: str
    latitude: float
    longitude: float
    url: str
    start: str
    timezone: str
    mid: str
    map: Map

    @staticmethod
    def directory() -> str: return "events"

    @classmethod
    def refresh(cls, storage: Storage, event: Dict[str, any], refresh_map: bool = False) -> "Event":
        
        country = Event.extract_country(event=event)
        uuid = Event.extract_uuid(event=event)
        coordinate = Event.extract_coordinate(event=event)

        mid=Event.extract_mid(soup=cls.soup(url=os.path.join(url, "course")))

        if refresh_map or not Map.exists(storage=storage, uuid=uuid):
            map = Map.scrape(storage=storage, uuid=uuid, mid=mid)
        else:
            map = Map.get(storage=storage, uuid=uuid)

        data = Event(
            uuid=uuid,
            country=country.name.replace("_", " "),
            name=event["properties"]["EventShortName"],
            area=event["properties"]["EventLocation"],
            latitude=coordinate.latitude,
            longitude=coordinate.longitude,
            url=event["url"],
            start=Event.extract_start(soup=cls.soup(url=event["url"])),
            timezone=coordinate.timezone,
            mid=mid,
            map=map
        )

        data.write(storage=storage, uuid=uuid)

        return data

    @classmethod
    def get(cls, storage: Storage, event: Dict[str, any]) -> "Stored":
    
        uuid = Event.extract_uuid(event=event)

        return super().get(storage=storage, uuid=uuid)

    @staticmethod
    def extract_country(event: Dict[str, any]) -> Country:

        try:
            return Country(event["properties"]["countrycode"])
        except ValueError:
            raise UnsupportedCountryError(event["properties"]["countrycode"])

    @staticmethod    
    def extract_uuid(event: Dict[str, any]) -> str:

        country = Event.extract_country(event=event)

        return str(uuid5(uuid_namespace, name=f"{country.value}|{event['id']}"))

    @staticmethod
    def extract_coordinate(event: Dict[str, any]) -> Coordinate:

        return Coordinate(
            latitude=event["geometry"]["coordinates"][1],
            longitude=event["geometry"]["coordinates"][0]
        )

    @staticmethod    
    def extract_start(soup: BeautifulSoup) -> str:
        
        content = soup.select_one("div#main div.homeleft")

        index = [h.text.strip() for h in content.select("h4")].index("When is it?")
        text = [p.text.strip() for p in content.select("p.paddetandb")][index]
        time = re.search(r"(\d{1,2}):(\d{2})", text)
        
        return f"{int(time.group(1)):02d}:{time.group(2)}"
    
    @staticmethod
    def extract_mid(soup: BeautifulSoup) -> str:
        
        params = dict([tuple(p.split("=")) for p in soup.select_one("iframe").attrs["src"].split("?")[1].split("&")])
        
        return params["mid"]

    def minify(self) -> "EventMini":

        return EventMini.minify(event=self)


@dataclass
class EventMini:

    uuid: str
    latitude: float
    longitude: float
    name: str
    country: str
    start: str
    timezone: str

    @classmethod
    def minify(cls, event: Event) -> "EventMini":

        return EventMini(
            uuid=event.uuid,
            latitude=event.latitude,
            longitude=event.longitude,
            name=event.name,
            country=event.country,
            start=event.start,
            timezone=event.timezone
        )

    def json(self) -> Dict[str, any]:

        return self.__dict__

    @property
    def state(self) -> str:

        return str(uuid5(uuid_namespace, name="|".join([self.uuid, self.name, self.start, self.timezone])))
