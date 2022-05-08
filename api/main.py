# !/usr/bin/env python
# -*- coding: utf-8 -*-

import flask

from models.api import Response
from models.runner import Runner


def get_runner(request: flask.Request):

    try:
        runner = Runner.scrape(number=request.json["number"])

    except Exception as e:  # pylint: disable=W0703
        print(e)
        return Response.error(error="An error occured", exception=e)

    else:
        return Response.ok(data=runner)


def get_runner_remote(request: flask.Request):

    try:
        runner = Runner.remote_scrape(number=request.json["number"], content=request.json["content"])

    except Exception as e:  # pylint: disable=W0703
        print(e)
        return Response.error(error="An error occured", exception=e)

    else:
        return Response.ok(data=runner)
