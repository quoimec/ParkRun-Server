# !/usr/bin/env python
# -*- coding: utf-8 -*-

from models.event import Event
from models.master import Master

from utils.storage import Storage

storage = Storage(bucket="parkrun-au")

for event in Master.base():

    _ = Event.refresh(storage=storage, event=data)

Master.refresh(storage=storage)
