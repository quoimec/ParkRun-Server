# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from typing import List
from dataclasses import dataclass

from .base import Scraped


@dataclass
class Coordinate(Scraped):
    
    latitude: float
    longitude: float
    
    @staticmethod
    def extract(data: str) -> "Coordinate":
        
        data = data.strip()
        
        if data == "":
            return None
        
        data = data.split(",")
        
        return Coordinate(
            latitude=float(data[1]),
            longitude=float(data[0])
        )
    
    @property
    def timezone(self) -> str:
        
        if not hasattr(self, "_timezone_"):
        
            if "TIMEZONE_DB_API_KEY" in os.environ:

                url = "http://api.timezonedb.com/v2.1/get-time-zone"

                params = {
                    "key": os.environ["TIMEZONE_DB_API_KEY"],
                    "format": "json",
                    "by": "position",
                    "lat": self.latitude,
                    "lng": self.longitude,
                    "fields": ",".join(["zoneName"])
                }

                self._timezone_ = self.http_get(url, params=params).json()["zoneName"]

                time.sleep(1)

            else:

                from timezonefinder import TimezoneFinder

                tf = TimezoneFinder()
                self._timezone_ = tf.timezone_at(lng=self.longitude, lat=self.latitude)  
            
        return self._timezone_

    def json(self) -> List[float]:

        return [self.latitude, self.longitude]   
