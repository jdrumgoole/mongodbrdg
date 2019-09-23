import unittest
from datetime import datetime
import pymongo

from mongodbrdg.randomdata import User, Sessions
from mongodbrdg.inserter import Inserter

class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._client = pymongo.MongoClient()
        self._db = self._client["rdgtest"]
        self._users = self._db["users"]
        self._sessions = self._db["sessions"]
        self._user_inserter = Inserter(self._users)
        self._session_inserter = Inserter(self._sessions)

    def tearDown(self) -> None:
        self._client.drop_database("rdgtest")

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
        for i in users.make_users(100):
            self._user_inserter.insert(i)
        self._user_inserter.flush()
        self.assertEqual(self._users.count_documents({}), 100)

    def test_sessions(self):

        user = User().make_one_user()
        self._user_inserter.insert(user, flush=True)
        s = Sessions(user)
        for i, j in s.make_sessions(20):
            self._session_inserter.insert(i)
            self._session_inserter.insert(j)
            self.assertGreater(j["logout"], i["login"])

        self._session_inserter.flush()

        self.assertEqual( 20 * 2, self._sessions.count_documents({}))



if __name__ == '__main__':
    unittest.main()
