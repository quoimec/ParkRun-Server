# !/usr/bin/env python
# -*- coding: utf-8 -*-

import enum


class UnsupportedCountryError(Exception): pass

class Country(enum.Enum):

    Australia = 3
    # New_Zealand = 65
    # South_Africa = 85
    