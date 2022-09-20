# !/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
import base64
import zipfile
import polyline

import pandas as pd

from PIL import Image
from typing import List, Dict
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from collections import namedtuple
from dataclasses import dataclass

from utils.storage import Storage
from utils.uuid_ import generate_uuid

from .event import Event
from .exceptions import MapMatchError
from .base import Scraped, Stored, ExpiredVersionError


@dataclass
class Coordinate():

    latitude: float
    longitude: float

    def json(self) -> List[float]:

        return [self.latitude, self.longitude]


@dataclass
class Course(Scraped, Stored):

    uuid: str
    mid: str
    image: str
    start: Coordinate
    finish: Coordinate
    route: List[Coordinate]

    version: str = "1.0.0"

    @staticmethod
    def directory() -> str: return "maps"

    def generate_state(self) -> str: return generate_uuid(data=str(self.__dict__))

    @classmethod
    def refresh(cls, storage: Storage, uuid: str, mid: str) -> "Course":

        response = cls.http_get(url=f"https://www.google.com/maps/d/kml?mid={mid}")

        with zipfile.ZipFile(io.BytesIO(response.content)).open("doc.kml") as kml:

            soup = BeautifulSoup(kml.read(), features="html.parser")

        point_placemarks = Course.extract_placemarks(soup=soup, point=True)
        route_placemarks = Course.extract_placemarks(soup=soup, point=False)

        # "": [""],  # 

        special = {
            "9a372327-e977-5a01-88ec-cc646120261a": ["run/walk along esplanade concrete foot path"],  # Cairns
            "1e2bcdc7-6107-515c-b8f4-31cc2e22998c": ["2.5km"],  # Cronulla
            "09fa28f9-7de3-5959-8752-afaddd789cb5": ["line 1"],  # North Parkes Oval
            "c1e18aaa-2b94-5553-8868-332011a7e5e4": ["line 3"],  # North Bay
            "83036295-3ec7-54ee-a70a-f51f4022f404": ["oldbridge"],  # Oldbridge
            "29a4bd35-0cc3-5aac-8990-887a28938b06": ["run.gpx"],  # Norm-Hudlin Trails
            "666d34c0-6553-5284-bc8d-671ee3f9336c": ["line 3"],  # Somerset West
            "f0730b89-eff2-5573-b0e0-8dee0a2dd5d5": ["line 1"],  # Congleton
            "30e45a6b-9070-5842-bcb8-dd2a13f3771c": ["line 1"],  # Worsley Woods - Bad, needs multiple lines
            "8acf8f6e-916a-594b-83b1-c0c84de38067": ["blue lap"],  # Gateshead
            "2be4d9ca-5018-50f5-8eb2-0b043be6043b": ["line 1"],  # Southend
            "eadaceea-7f90-5d27-ac83-1df0a77f1955": ["run"],  # Aldenham
            "97a49a2c-390b-50d8-9962-95180984a167": ["line 2"],  # Millennium Country
            "62079efd-bfa5-5dd0-ab8c-92455dbd258f": ["line 1"],  # Bryn Bach
            "b3db1d16-7585-5817-b9b2-751fd52087a1": ["perimeter lap"],  # Aberystwyth
            "24b4bf54-794a-518a-9b88-8f571134c123": ["track 1"],  # Forest Rec
            "fcf7c069-ba45-5552-b4c5-52d6890b446e": ["large lap"],  # Wallace
            "6abcbd07-8e46-50b4-b725-a341a4baee95": ["line 1"],  # Barnstaple
            "9641f1a9-7ce7-57ab-a549-715ded8cbae1": ["lap 1"],  # Preston Park
            "3967a0e6-144e-58d0-94b8-a69d789f4c70": ["laps 2-4"],  # Dewsbury
            "cf6d3f58-34a5-5db6-b50f-448877c94b3d": ["line 5"],  # Armley
        }

        route = route_placemarks[Course.extract_match(
            keys=route_placemarks.keys(),
            bank=[r"^route$", r"^course$", "route", "course", "parkrun"] + special.get(uuid, [])
        )]

        if len(point_placemarks) == 0:
            point_placemarks = {
                "start": route[0],
                "finish": route[-1]
            }

        start = point_placemarks[Course.extract_match(
            keys=point_placemarks.keys(),
            bank=[r"^start$", "start/finish", "start / finish", r"^finish$", "start", "finish"]
        )]

        finish = point_placemarks[Course.extract_match(
            keys=point_placemarks.keys(),
            bank=[r"^finish$", "start/finish", "start / finish", r"^start$", "finish", "start"]
        )]

        data = Course(
            uuid=uuid,
            mid=mid,
            image=Course.extract_image(start=start, finish=finish, route=route),
            start=start,
            finish=finish,
            route=route
        )

        data.write(storage=storage, uuid=uuid)

        return data

    @classmethod
    def get(cls, storage: Storage, event: Event) -> "Course":

        try:
            raw = super().get(storage=storage, uuid=event.uuid)

            if raw.get("version") != Course.version: raise ExpiredVersionError()

            for key in ["state", "refreshed"]:
                if key in raw: del raw[key]

        except FileNotFoundError:
            course = Course.refresh(storage=storage, uuid=event.uuid, mid=event.mid)

        except ExpiredVersionError:
            course = getattr(cls, f"migrate_v{Course.version.replace('.', '_')}")(event=event, raw=raw)
            course.write(storage=storage, uuid=event.uuid)

        else:

            # Convert the lists back into Coodinates
            raw["start"] = Coordinate(*raw["start"])
            raw["finish"] = Coordinate(*raw["finish"])
            raw["route"] = [Coordinate(*c) for c in raw["route"]]

            course = Course(**raw)

        return course

    @staticmethod
    def extract_placemarks(soup: BeautifulSoup, point: bool) -> Dict[str, any]:

        empty_default = namedtuple("Coordinates", ["text"])

        placemarks = [(n, c) for (n, c) in [
            (placemark.select_one("name").text.lower(), [
                coordinate
                for coordinate in [
                    Course.extract_coordinate(data=data)
                    for data in (placemark.select_one("coordinates") or empty_default(text="")).text.split("\n")
                ] if coordinate is not None
            ])
            for placemark in soup.select("placemark")
        ] if len(c) > 0]

        if point:

            return {
                name: coordinates[0]
                for name, coordinates in placemarks
                if len(coordinates) == 1
            }

        else:

            return {
                name: coordinates
                for name, coordinates in placemarks
                if len(coordinates) > 1
            }

    @staticmethod
    def extract_match(keys: List[str], bank: List[str]) -> str:

        for regex in bank:

            for key in keys:

                match = re.search(regex, key)

                if match is not None:
                    return key

        raise MapMatchError(f"Unable to find a suitable key match: keys: {keys} - bank: {bank}")

    @staticmethod
    def extract_coordinate(data: str) -> "Coordinate":

        data = data.strip()

        if data == "":
            return None

        data = data.split(",")

        return Coordinate(
            latitude=float(data[1]),
            longitude=float(data[0])
        )

    @staticmethod
    def extract_midpoint(route: List[Coordinate]) -> Coordinate:

        df = pd.DataFrame([c.json() for c in route], columns=["latitude", "longitude"])

        return Coordinate(
            latitude=round(min(df["latitude"]) + ((max(df["latitude"]) - min(df["latitude"])) / 2), 6),
            longitude=round(min(df["longitude"]) + ((max(df["longitude"]) - min(df["longitude"])) / 2), 6)
        )

    @staticmethod
    def extract_zoom(midpoint: Coordinate, route: List[Coordinate]) -> int:

        def zoom(delta: float) -> int:

            if delta <= 0.005757:
                return 16
            elif delta <= 0.011048:
                return 15
            else:
                return 14

        # Latitude
        top_zoom = zoom(delta=max([c.latitude for c in route]) - midpoint.latitude)
        bottom_zoom = zoom(delta=midpoint.latitude - min([c.latitude for c in route]))

        # Longitude
        left_zoom = zoom(delta=midpoint.longitude - min([c.longitude for c in route]))
        right_zoom = zoom(delta=max([c.longitude for c in route]) - midpoint.longitude)

        return min(top_zoom, bottom_zoom, left_zoom, right_zoom)

    @staticmethod
    def extract_image(start: Coordinate, finish: Coordinate, route: List[Coordinate], size: int = 1280, crop: int = 40):

        if "GCLOUD_MAPS_KEY" not in os.environ:
            load_dotenv()

        key = os.environ["GCLOUD_MAPS_KEY"]

        midpoint = Course.extract_midpoint(route=route)
        zoom = Course.extract_zoom(midpoint=midpoint, route=route)

        if len(route) > 1000:
            keep = int(len(route) / 1000)
            route = [point for (index, point) in enumerate(route) if index % keep == 0 or index in [0, len(route) - 1]]

        marker_start = f"color:0xDC6259|size:mid|label:S|{start.latitude},{start.longitude}"
        marker_finish = f"color:0xDC6259|size:mid|label:F|{finish.latitude},{finish.longitude}"  # pylint: disable=W0612
        course_path = f"color:0x0000ff|weight:5|enc:{polyline.encode([(point.latitude, point.longitude) for point in route], 5)}"

        url = f"https://maps.googleapis.com/maps/api/staticmap?center={midpoint.latitude},{midpoint.longitude}&zoom={zoom}&size={size}x{size}&scale=2&path={course_path}&markers={marker_start}&map_id=f8f6d8abd5bb9aee&key={key}"

        response = Scraped.http_get(url=url)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content)).crop((crop, crop, size - crop, size - crop))

        with io.BytesIO() as output:
            image.save(output, format="PNG")
            content = output.getvalue()

        return base64.b64encode(content).decode("utf8")

    @staticmethod
    def migrate_v1_0_0(event: Event, raw: Dict[str, any]) -> "Course":

        start = Coordinate(*raw["start"])
        finish = Coordinate(*raw["finish"])
        route = [Coordinate(*c) for c in raw["path"]]

        return Course(
            uuid=event.uuid,
            mid=raw["mid"],
            image=Course.extract_image(start=start, finish=finish, route=route),
            start=start,
            finish=finish,
            route=route
        )
