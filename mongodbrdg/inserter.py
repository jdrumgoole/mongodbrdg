from typing import List, Dict

import pymongo


class Inserter:

    def __init__(self, c:pymongo.collection, bucket_size:int = 100):
        self._col:pymongo.collection = c
        self._bucket_size = bucket_size
        self._bucket:List = []

    def insert(self, doc:Dict, flush:bool=False):
        self._bucket.append(doc)
        if (len(self._bucket) % self._bucket_size == 0) or flush:
            self.flush()

    def flush(self):
        if len(self._bucket) > 0:
            self._col.insert_many(self._bucket)
            self._bucket = []
