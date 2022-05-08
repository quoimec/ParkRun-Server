# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

from dataclasses import dataclass
from typing import List, Dict, Generator
from uuid import uuid5, NAMESPACE_URL as uuid_namespace

from utils.storage import Storage

from .base import Scraped, Stored
from .event import Event, EventMini
from .country import UnsupportedCountryError


@dataclass
class State(Scraped, Stored):

    state: str
    refreshed: datetime.datetime

    @staticmethod
    def directory() -> str: return ""

    @classmethod
    def refresh(cls, storage: Storage, master: "Master") -> "State":

        state = State(
            state=master.state,
            refreshed=master.refreshed
        )

        state.write(storage=storage, uuid="state")

        return state


@dataclass
class Master(State):

    events: List[EventMini]

    @classmethod
    def base(cls) -> Generator[Dict[str, any], None, None]:

        data = cls.http_get(url="https://images.parkrun.com/events.json").json()

        countries = data["countries"]

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

        events = []

        for e in cls.base():

            try:
                events.append(Event.get(storage=storage, event=e).minify())
            except Exception as ee:
                print(e)
                print(ee)

        master = Master(
            events=events,
            state=Master.extract_state(events=events),
            refreshed=datetime.datetime.now()
        )

        master.write(storage=storage, uuid="master")

        _ = State.refresh(storage=storage, master=master)

        return master

    @staticmethod
    def extract_state(events: List[EventMini]) -> str:

        return str(uuid5(uuid_namespace, name="|".join(e.state for e in events)))
