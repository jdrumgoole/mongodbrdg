from datetime import datetime
from typing import List, Dict

import pymongo


class BlockInserter:

    def __init__(self, c: pymongo.collection, bucket_size: int = 1000):
        self._col: pymongo.collection = c
        self._bucket_size = bucket_size
        self._bucket: List = []
        self._count = 0
        self._start_time = None
        self._stop_time = None

    def start_timer(self):
        self._start_time = datetime.utcnow()
        self._stop_time = None

    def elapsed(self):
        if self._stop_time:
            return self._stop_time - self._start_time
        else:
            return datetime.utcnow() - self._start_time

    def stop_timer(self):
        self._stop_time = datetime.utcnow()
        return self._stop_time - self._start_time

    def insert_one(self, doc: Dict, flush: bool = False) -> int:
        inserted_count = 0
        self._bucket.append(doc)
        if (len(self._bucket) % self._bucket_size == 0) or flush:
            inserted_count = self.flush()
        return inserted_count

    def insert_many(self, docs: list[Dict], flush: bool = False) -> int:
        inserted_count = 0
        self._bucket.extend(docs)
        if (len(self._bucket) >= self._bucket_size) or flush:
            inserted_count = self.flush()
            self._count = self._count + inserted_count
        return inserted_count

    def flush(self) -> int:
        inserted_count = 0
        if len(self._bucket) > 0:
            self._col.insert_many(self._bucket)
            inserted_count = len(self._bucket)
            self._bucket = []
        return inserted_count
