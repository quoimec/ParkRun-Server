# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from bs4 import BeautifulSoup


class Scraped():
    
    class NoResultsError(Exception): pass
    
    @classmethod
    def http_get(cls, url: str, **kwargs) -> requests.models.Response:
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }

        response = requests.get(url, headers=headers, **kwargs)
   
        return response
    
    @classmethod
    def soup(cls, url: str) -> BeautifulSoup:
    
        return BeautifulSoup(cls.http_get(url=url).content, features="html.parser")