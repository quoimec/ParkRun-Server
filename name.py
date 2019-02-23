#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import lxml
from bs4 import BeautifulSoup
import json

def getName(request):

    runnerID = "5470914"
    baseURL = "http://www.parkrun.com.au/results/athleteresultshistory/?athleteNumber="

    userHeader = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }

    httpResponse = requests.get(baseURL + runnerID, headers = userHeader)

    if httpResponse.status_code != 200:
        return json.dumps({"name": None, "status": str(httpResponse.status_code)})

    soupData = BeautifulSoup(httpResponse.text, "lxml")

    if soupData != None:

        runnerName = soupData.find("h2").text.split(" (")[0].title()

        return json.dumps({"name": runnerName})

    else:

        return json.dumps({"name": None, "message": "Soup data empty"})
