import unittest

import pymongo

from mongodbrdg.randomuser import User
from mongodbrdg.threadinserter import ThreadedInserter


class TestThreading(unittest.TestCase):

    def setUp(self) -> None:
        self._client = pymongo.MongoClient()
        self._db = self._client["RDGTEST"]
        self._users = self._db["users"]

    def tearDown(self) -> None:
        self._client.drop_database("RDGTEST")
        pass

    def test_single_inserter(self):
        u = User()
        try:
            t = ThreadedInserter(c=self._users, doc_generator=u)
            t.start(thread_count=1, user_count=20)
            t.stop()
        except pymongo.errors.BulkWriteError as e:
            print(f"{e}")
            t.stop()

    def test_threaded_inserter(self):
        u = User()
        try:
            t = ThreadedInserter(c=self._users,doc_generator=u)
            t.start(thread_count=2, user_count=20)
            t.stop()
        except pymongo.errors.BulkWriteError as e:
            print(f"{e}")
            raise


if __name__ == '__main__':
    unittest.main()
