# !/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json

from typing import List, Dict, Tuple

from utils.json import JSONEncoder
from utils.storage import Storage, Codable


class Stored():
    
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
    def get(cls, storage: Storage, uuid: str) -> "Stored":
    
        file, directory = cls.path(uuid=uuid)

        return cls(**json.loads(
            storage.get(file=file, directory=directory)
        ))

    @classmethod
    def delete(cls, storage: Storage, uuid: str):

        file, directory = cls.path(uuid=uuid)

        storage.delete(file=file, directory=directory)

    @abc.abstractmethod
    def refresh(self, storage: Storage, *args, **kwargs) -> "Stored":  raise NotImplementedError
    
    def write(self, storage: Storage, uuid: str):

        file, directory = self.path(uuid=uuid)

        with storage.write(file=file, directory=directory, codable=Codable.json) as blob:
            blob.write(json.dumps(self, cls=JSONEncoder))
        
    def json(self) -> Dict[str, any]:
        
        return self.__dict__