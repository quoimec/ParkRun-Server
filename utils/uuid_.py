# !/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid5, NAMESPACE_URL as uuid_namespace

def generate_uuid(data: str) -> str:

    return str(uuid5(uuid_namespace, name=data))
