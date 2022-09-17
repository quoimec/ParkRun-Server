# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import abc
import copy
import json
import datetime

from typing import Dict, Tuple

from utils.json_ import JSONEncoder
from utils.storage import Storage, Codable


class ExpiredVersionError(Exception): pass


class Stored():

    @staticmethod
    @abc.abstractmethod
    def directory() -> str: raise NotImplementedError

    @classmethod
    def path(cls, uuid: str) -> Tuple[str]:

        return (f"{uuid}.json", cls.directory())

    @classmethod
    def exists(cls, storage: Storage, uuid: str) -> bool:

        file, directory = cls.path(uuid=uuid)

        return storage.exists(file=file, directory=directory)

    @classmethod
    def get(cls, storage: Storage, uuid: str) -> Dict[str, any]:

        file, directory = cls.path(uuid=uuid)

        data = storage.get(file=file, directory=directory)

        if data is None or data == "":
            raise FileNotFoundError()

        return json.loads(data)

    @classmethod
    def delete(cls, storage: Storage, uuid: str):

        file, directory = cls.path(uuid=uuid)

        storage.delete(file=file, directory=directory)

    @abc.abstractmethod
    def refresh(self, storage: Storage, *args, **kwargs) -> "Stored":  raise NotImplementedError

    def write(self, storage: Storage, uuid: str):

        file, directory = self.path(uuid=uuid)

        storage.write(file=file, data=json.dumps(self, cls=JSONEncoder), directory=directory, codable=Codable.json)

    def json(self) -> Dict[str, any]:

        data = copy.copy(self.__dict__)

        private_values = [key for key in data.keys() if re.search(r"_(\w)+_", key) is not None]

        for key in private_values:
            del data[key]

        if hasattr(self, "generate_state"):
            data["state"] = getattr(self, "generate_state")()

        data["refreshed"] = datetime.datetime.now()

        return data
