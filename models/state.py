# !/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from utils.storage import Storage

from .base import Stored
from .event import Event
from .course import Course


@dataclass
class State(Stored):

    uuid: str
    event: str
    course: str

    @staticmethod
    def directory() -> str: return "state"

    @classmethod
    def refresh(cls, storage: Storage, event: Event, course: Course) -> "State":

        state = State(
            uuid=event.uuid,
            event=event.generate_state(),
            course=course.generate_state()
        )

        state.write(storage=storage, uuid=event.uuid)

        return state

@dataclass
class MasterState(Stored):

    state: str

    @staticmethod
    def directory() -> str: return "state"

    @classmethod
    def refresh(cls, storage: Storage, master: "Master", uuid: str) -> "MasterState":

        state = MasterState(
            state=master.state
        )

        state.write(storage=storage, uuid=uuid)

        return state
