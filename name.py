#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import lxml
from bs4 import BeautifulSoup
import json

def getName(request):

    def getSoup(passedURL):

        userHeader = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive"
        }

        httpResponse = requests.get(passedURL, headers = userHeader)

        if httpResponse.status_code != 200 or len(httpResponse.history) > 0:
            return None

        soupData = BeautifulSoup(httpResponse.text, "lxml")

        return soupData

    runnerID = "5470914"
    baseURL = "http://www.parkrun.com.au/results/athleteresultshistory/?athleteNumber="
    soupData = getSoup(self.baseURL + self.runnerID)

    if soupData == None:

        runnerName = soupData.find("h2").text.split(" (")[0].title()

        return make_response(jsonify({"name": runnerName}), 200)

    else:

        return make_response(jsonify("", 404))
