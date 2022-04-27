# !/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import enum
import zipfile

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Tuple

from utils.storage import Storage

from .base import Scraped, Stored
from .coordinate import Coordinate


@dataclass
class Map(Scraped, Stored):
    
    mid: str
    start: Coordinate
    finish: Coordinate
    path: List[Coordinate]

    @staticmethod
    def directory() -> str: return "maps"

    @classmethod
    def refresh(cls, storage: Storage, uuid: str, mid: str) -> "Map":

        response = cls.http_get(url=f"https://www.google.com/maps/d/kml?mid={mid}")
        
        with zipfile.ZipFile(io.BytesIO(response.content)).open("doc.kml") as kml:
    
            soup = BeautifulSoup(kml.read(), features="html.parser")

        point_placemarks = Map.extract_placemarks(soup=soup, point=True)
        route_placemarks = Map.extract_placemarks(soup=soup, point=False)

        special = {
            "9a372327-e977-5a01-88ec-cc646120261a": ["run/walk along esplanade concrete foot path"],  # Cairns
            "1e2bcdc7-6107-515c-b8f4-31cc2e22998c": ["2.5km"],  # Cronulla
            "09fa28f9-7de3-5959-8752-afaddd789cb5": ["line 1"]  # North Parkes Oval
        }

        path = route_placemarks[Map.extract_match(
            keys=route_placemarks.keys(), 
            bank=[r"^route$", r"^course$", "route", "course", "parkrun"] + special.get(uuid, [])
        )]

        if len(point_placemarks) == 0:
            point_placemarks = {
                "start": path[0],
                "finish": path[-1]
            }

        data = Map(
            mid=mid,
            start=point_placemarks[Map.extract_match(
                keys=point_placemarks.keys(), 
                bank=[r"^start$", "start/finish", "start / finish", r"^finish$", "start", "finish"]
            )],
            finish=point_placemarks[Map.extract_match(
                keys=point_placemarks.keys(), 
                bank=[r"^finish$", "start/finish", "start / finish", r"^start$", "finish", "start"]
            )],
            path=path
        )

        data.write(storage=storage, uuid=uuid)

        return data

    @staticmethod
    def extract_placemarks(soup: BeautifulSoup, point: bool) -> Dict[str, any]:

        placemarks = [
            (placemark.select_one("name").text.lower(), [
                coordinate 
                for coordinate in [
                    Coordinate.extract(data=data) 
                    for data in placemark.select_one("coordinates").text.split("\n")
                ] if coordinate is not None
            ])
            for placemark in soup.select("placemark")
        ]

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

        raise Exception(f"Unable to find a suitable key match: keys: {keys} - bank: {bank}")
