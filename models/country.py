# !/usr/bin/env python
# -*- coding: utf-8 -*-

import enum


class UnsupportedCountryError(Exception): pass

class Country(enum.Enum):

    Australia = 3
    # Austria = 4
    Canada = 14
    # Denmark = 23
    # Finland = 30
    # France = 31
    # Germany = 32
    Ireland = 42
    # Italy = 44
    # Japan = 46
    # Malaysia = 57
    # Netherlands = 64
    New_Zealand = 65
    # Norway = 67
    # Poland = 74
    # Singapore = 82
    South_Africa = 85
    # Sweeden = 88
    United_Kingdom = 97
    United_States = 98

    def display(self) -> str:

        return self.name.replace("_", " ")
