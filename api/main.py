# !/usr/bin/env python
# -*- coding: utf-8 -*-

import flask

from models.api import Response
from models.runner import Runner


def get_runner(request: flask.Request):
    
    try:
        data = request.get_json()
        runner = Runner.scrape(number=data["number"])

    except Exception as e:
        return Response.error(error="An error occured", exception=e)

    else:
        return Response.ok(data=runner)
