# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import enum
import json

from dataclasses import dataclass
from typing import Dict, Callable
from google.oauth2 import service_account
from google.cloud import storage, exceptions


class Auth:
    
    @classmethod
    def credentials(cls, key: str = "GCLOUD_MASTER_SA_KEY"):
        
        if key in os.environ:
            data = json.loads(os.environ[key])
        else:
            with open(f"{key.lower()}.json") as file:
                data = json.load(file)
                
        return service_account.Credentials.from_service_account_info(data)

@dataclass
class Format:
    
    encode: str
    decode: Callable
        
        
class Codable(enum.Enum):

    text = Format(
        encode="plain/text",
        decode=lambda blob: blob.read()
    )

    json = Format(
        encode="application/json",
        decode=lambda blob: json.load(blob)
    )

class Storage(Auth):

    def __init__(self, bucket: str):

        self.client = storage.Client(
            credentials=self.credentials()
        )
        
        self.bucket = self.client.get_bucket(bucket)

    def get(self, file: str, directory: str = "", codable: Codable = Codable.text) -> any:

        path = os.path.join(directory, file)

        try:

            with self.bucket.blob(path).open(mode="r") as blob:
                return codable.value.decode(blob=blob)

        except exceptions.NotFound:
            raise FileNotFoundError(path)

    def write(self, file: str, directory: str = "", codable: Codable = Codable.text):
        
        path = os.path.join(directory, file)
        
        return self.bucket.blob(path).open(mode="w", content_type=codable.value.encode)

    def exists(self, file: str, directory: str = "") -> bool:
        
        path = os.path.join(directory, file)
        
        return self.bucket.blob(path).exists()

    def delete(self, file: str, directory: str = ""):

        path = os.path.join(directory, file)

        self.bucket.blob(path).delete()