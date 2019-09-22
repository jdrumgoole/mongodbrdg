import unittest
from datetime import datetime

from mongodbrdg.randomdata import RandomUser, RandomSessions

class MyTestCase(unittest.TestCase):

    def test_random_user(self):
        clone = RandomUser().make_user()
        self.assertTrue(clone is not None)

    def test_random_time(self):

        now=datetime.utcnow()
        future_time =RandomSessions.future_random_time(now, basis=0)
        self.assertEqual(now, future_time)

        future_time =RandomSessions.future_random_time(now, seconds = 5, basis=1)
        self.assertGreater(future_time, now)

    def test_sessions(self):

        r = RandomSessions(user_id=25, start_time = datetime.utcnow())
        for i, j in r.make_sessions(100):
            self.assertGreater(j["logout"], i["login"])



if __name__ == '__main__':
    unittest.main()
