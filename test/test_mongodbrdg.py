import unittest
from datetime import datetime
import pymongo

from mongodbrdg.randomdata import User, Sessions
from mongodbrdg.inserter import Inserter

class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._client = pymongo.MongoClient()
        self._db = self._client["RDGTEST"]
        self._users = self._db["users"]
        self._sessions = self._db["sessions"]
        self._user_inserter = Inserter(self._users)
        self._session_inserter = Inserter(self._sessions)

    def tearDown(self) -> None:
        self._client.drop_database("RDGTEST")
        pass

    def test_random_user(self):
        clone = User().make_one_user(1)
        self.assertTrue(clone is not None)

    def test_random_time(self):

        now=datetime.utcnow()
        future_time =Sessions.future_random_time(now, basis=0)
        self.assertEqual(now, future_time)

        future_time =Sessions.future_random_time(now, seconds = 5, basis=1)
        self.assertGreater(future_time, now)

    def test_insert(self):
        users = User()
        for i in users.make_users():
            self._user_inserter.insert(i)
        self._user_inserter.flush()
        self.assertEqual(self._users.count_documents({}), users.size)

    def test_insert_id_range(self):
        users = User(user_id_start=100, user_id_end=200)
        for i in users.make_users():
            self._user_inserter.insert(i)
        self._user_inserter.flush()
        self.assertEqual(self._users.count_documents({}), 100)
        self.assertEqual( 100, len(list(self._users.find({"user_id" :{ "$gte" : 100,
                                                                       "$lte" : 200}}))))

    def test_insert_date_range(self):
        users = User(user_id_end=1000, start_year=1990,end_year=1992)
        for i in users.make_users():
            self._user_inserter.insert(i)
        self._user_inserter.flush()
        self.assertEqual(self._users.count_documents({}), users.size)
        self.assertFalse(self._users.find_one({"registered": {"$lt" : datetime(year=1990, month=1, day=1)}}))
        self.assertTrue(self._users.find_one({"registered": {"$gt" : datetime(year=1990, month=1, day=3),
                                                             "$lt" : datetime(year=1993, month=1, day=1)}}))

    def test_sessions(self):

        user = User().make_one_user()
        self._user_inserter.insert(user, flush=True)
        s = Sessions(user, total=20)
        for i, j in s.make_sessions():
            self._session_inserter.insert(i)
            self._session_inserter.insert(j)
            self.assertGreater(j["logout"], i["login"])

        self._session_inserter.flush()

        self.assertEqual(s.total_documents, self._sessions.count_documents({}))



if __name__ == '__main__':
    unittest.main()
