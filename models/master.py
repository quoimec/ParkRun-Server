# !/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from dataclasses import dataclass
from typing import List, Dict, Tuple, Generator
from uuid import uuid5, NAMESPACE_URL as uuid_namespace

from utils.storage import Storage

from .base import Scraped, Stored
from .event import Event, EventMini
from .country import Country, UnsupportedCountryError


@dataclass
class Master(Scraped, Stored):

    events: List[EventMini]
    state: str
    refreshed: datetime.datetime

    @staticmethod
    def directory() -> str: return ""

    @classmethod
    def base(cls) -> Generator[Dict[str, any]]:

        data = cls.http_get(url="https://images.parkrun.com/events.json").json()

        countries = base["countries"]

        for event in data["events"]["features"]:

            try:     
                country = Event.extract_country(event=event)
            except UnsupportedCountryError:
                continue

            if event["properties"]["seriesid"] != 1:
                continue

            event["url"] = "https://" + os.path.join(countries[str(country.value)]["url"], event["properties"]["eventname"])

            yield event 

    @classmethod
    def refresh(cls, storage: Storage) -> "Master":

        events = [EventMini(event=e) for e in cls.base()]

        data = Master(
            events=events,
            state=Master.extract_state(events=events),
            refreshed=datetime.datetime.now()
        )

        data.write(storage=storage, uuid="master")

        return data

    @staticmethod    
    def extract_state(events: List[EventMini]) -> str:

        return str(uuid5(uuid_namespace, name="|".join(e.uuid for e in events)))
