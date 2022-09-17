# !/usr/bin/env python
# -*- coding: utf-8 -*-

from models.event import Event
from models.course import Course
from models.master import Master

from utils.storage import Storage

storage = Storage(bucket="parkrun-au")

for data in Master.base():

    event = Event.get(storage=storage, data=data)
    course = Course.get(storage=storage, event=event)


    # _ = Event.refresh(storage=storage, event=data)

Master.refresh(storage=storage)
