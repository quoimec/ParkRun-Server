# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import dataclasses

class JSONEncoder(json.JSONEncoder):
    
    def default(self, value):

        if dataclasses.is_dataclass(value):
            return value.json()

        if isinstance(value, (datetime.datetime, datetime.date)):
            return value.isoformat()
        
        return super().default(value)