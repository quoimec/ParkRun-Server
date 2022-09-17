# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests

from bs4 import BeautifulSoup


class Scraped():

    class NoResultsError(Exception): pass

    @classmethod
    def http_get(cls, url: str, **kwargs) -> requests.models.Response:

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive"
        }

        response = requests.get(url, headers=headers, **kwargs)

        time.sleep(2)

        return response

    @classmethod
    def soup(cls, url: str) -> BeautifulSoup:

        return BeautifulSoup(cls.http_get(url=url).content, features="html.parser")

    @classmethod
    def soup_remote(cls, content: str) -> BeautifulSoup:

        return BeautifulSoup(content, features="html.parser")
