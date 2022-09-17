# !/usr/bin/env python
# -*- coding: utf-8 -*-

from models.event import Event
from models.master import Master

from utils.storage import Storage

storage = Storage(bucket="parkrun-au")

class Migration_V1:

    def migrate_event(uuid: str):

        Event