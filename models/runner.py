# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from typing import Dict
from bs4 import BeautifulSoup
from dataclasses import dataclass

from .base import Scraped


@dataclass
class Runner(Scraped):

    number: str
    name: str
    runs: int
    fastest: str

    @classmethod
    def scrape(cls, number: str) -> "Runner":

        soup = cls.soup(url=f"https://www.parkrun.com.au/parkrunner/{number}/all/")

        return Runner(
            number=number,
            name=Runner.extract_name(soup=soup),
            runs=Runner.extract_runs(soup=soup),
            fastest=Runner.extract_fastest(soup=soup)
        )

    @classmethod
    def remote_scrape(cls, number: str, content: str) -> "Runner":

        soup = cls.soup_remote(content=content)

        return Runner(
            number=number,
            name=Runner.extract_name(soup=soup),
            runs=Runner.extract_runs(soup=soup),
            fastest=Runner.extract_fastest(soup=soup)
        )

    @staticmethod
    def extract_name(soup: BeautifulSoup) -> str:

        text = soup.select_one("h2").text.lower()
        names = []

        pres = {
            "o'": "O'",
            "d'": "D'"
        }

        for word in text.split(" "):

            if word[:2] in pres.keys():
                pre = pres[word[:2]]
                word = word[2:]
            else:
                pre = ""

            names.append(pre + "-".join([w.capitalize() for w in word.split("-")]))

        if len(names) == 0:
            return None

        return " ".join(names)

    @staticmethod
    def extract_runs(soup: BeautifulSoup) -> int:

        text = soup.select_one("h3")

        if text is not None:
            runs = re.match(r"(\d+)", text.text.strip()).group(0)
        else:
            runs = None

        return runs

    @staticmethod
    def extract_fastest(soup: BeautifulSoup) -> str:

        tables = soup.select("table", id="results")
        table = None

        for t in tables:

            if t.select_one("caption").text.strip() == "Summary Stats for All  Locations":
                table = t
        try:

            if table is None:
                raise Scraped.NoResultsError()

            column = [th.text.strip() for th in table.select_one("thead").select_one("tr").select("th")].index("Fastest")
            row = [tr.select("td")[0].text.strip() for tr in table.select_one("tbody").select("tr")].index("Time")

            fastest = table.select_one("tbody").select("tr")[row].select("td")[column].text.strip()

        except Scraped.NoResultsError:
            return None

        else:
            return fastest

    def json(self) -> Dict[str, any]:

        return self.__dict__
