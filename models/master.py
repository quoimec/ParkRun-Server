# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from dataclasses import dataclass
from typing import List, Dict, Iterator

from utils.storage import Storage
from utils.uuid_ import generate_uuid

from .base import Scraped, Stored
from .event import Event
from .exceptions import MapMatchError
from .course import Course
from .state import State, MasterState
from .country import UnsupportedCountryError


@dataclass
class Master(Scraped, Stored):

    uuid: str
    events: List[Event]
    state: str

    bucket: str
    _storage_: Storage

    def __enter__(self):

        return self

    def __exit__(self, type_, value, traceback):

        self.state = Master.extract_state(events=self.events)

        self.write(storage=self._storage_, uuid=self.uuid)

        _ = MasterState.refresh(storage=self._storage_, master=self, uuid=self.uuid)

    def __iter__(self) -> Iterator[Dict[str, any]]:

        json = self.http_get(url="https://images.parkrun.com/events.json").json()

        countries = json["countries"]

        for data in json["events"]["features"]:

            try:
                country = Event.extract_country(data=data)
            except UnsupportedCountryError:
                continue

            if data["properties"]["seriesid"] != 1:
                continue

            data["url"] = "https://" + os.path.join(countries[str(country.value)]["url"], data["properties"]["eventname"])

            yield data

    @staticmethod
    def directory() -> str: return ""

    @classmethod
    def refresh(cls, bucket: str, uuid: str = "master") -> "Master":

        master = Master(
            uuid=uuid,
            events=[],
            state=None,
            bucket=bucket,
            _storage_=Storage(bucket=bucket)
        )

        return master

    @staticmethod
    def extract_state(events: List[Event]) -> str:

        return generate_uuid(data="|".join(e.generate_state() for e in events))

    @classmethod
    def refresh_event(cls, bucket: str, data: Dict[str, any]) -> Event:

        storage = Storage(bucket=bucket)

        try:

            event = Event.get(storage=storage, data=data)
            course = Course.get(storage=storage, event=event)
            _ = State.refresh(storage=storage, event=event, course=course)

        except MapMatchError as e:

            return MapMatchError(f"uuid: {Event.extract_uuid(data)}, {data['url']}/course, {e}")

        except Exception as e:

            print(data)
            raise Exception(f"uuid: {Event.extract_uuid(data)}, {data['url']}") from e

        else:

            return event
