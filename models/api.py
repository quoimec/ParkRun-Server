# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from typing import Tuple

from utils.json_ import JSONEncoder


class Response:

    @classmethod
    def error(cls, error: str, exception: Exception, **kwargs) -> Tuple:

        return (
            json.dumps({
                "error": error,
                "exception": str(exception),
                **kwargs
            }, cls=JSONEncoder),
            400,
            {"Content-Type": "application/json"}
        )

    @classmethod
    def ok(cls, data: any) -> Tuple:

        try:

            return (
                json.dumps(data, cls=JSONEncoder),
                200,
                {"Content-Type": "application/json"}
            )

        except Exception as e:

            return cls.error(
                error="Unable to generate success response",
                exception=str(e)
            )
