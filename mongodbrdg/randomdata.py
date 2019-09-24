from datetime import timedelta
from mimesis import Generic
from mimesis.enums import Gender
import random
from datetime import datetime

class User:

    interests = ["Soccer", "Golf", "Football", "Stamp Collecting", "skydiving",
                 "Board gaming", "Darts", "Swimmming", "Triathlon", "Running",
                 "Reading", "politics"]

    def __init__(self, locale: str = "en",
                 user_id_start:int=0,
                 user_id_end:int=1000,
                 max_friends:int = 0,
                 start_year:int = None,
                 end_year:int = None,
                 seed: int = None) -> object:

        self._locale = locale
        self._seed = seed
        if self._seed:
            self._generic = Generic(self._locale, self._seed)
        else:
            self._generic = Generic(self._locale)

        self._user_id_start = user_id_start
        self._user_id_end = user_id_end
        self._max_friends = max_friends
        assert self._user_id_start < self._user_id_end

        if start_year is None:
            self._start_year = 2015
        else:
            self._start_year = start_year

        if end_year is None:
            self._end_year = 2019
        else:
            self._end_year = end_year


    @property
    def user_id_start(self):
        return self._user_id_start

    @property
    def user_id_end(self):
        return self._user_id_end

    @property
    def size(self):
        return self._user_id_end - self._user_id_start

    @property
    def start_year(self):
        return self._start_year

    @property
    def end_year(self):
        return self._end_year


    def make_friends(self):
        friends:set=set()
        for i in range(random.randint(0, self._max_friends)):
            friend = random.randint( self._user_id_start, self._user_id_end)
            friends.add(friend)
        return list(friends)

    def make_one_user(self, user_id:int=0):

        person = self._generic.person
        address = self._generic.address
        business = self._generic.business
        internet = self._generic.internet
        datetime = self._generic.datetime

        user = {}

        gender = random.choice(list(Gender))
        gender_string = str(gender).split(".")[1]
        user["first_name"] = person.name(gender)
        user["last_name"] = person.surname(gender)
        user["gender"] = gender_string
        user["company"] = business.company()
        email_domain = "".join(user['company'].lower().split(" "))
        user["email"] = f"{user['first_name']}.{user['last_name']}@{email_domain}{internet.top_level_domain()}"
        year = random.randint(2000, 2018)
        user["registered"] = datetime.datetime(start=self._start_year, end=self._end_year)
        user["user_id"] = self._user_id_start + user_id
        user["country"]= address.country()
        user["city"] = address.city()
        user["phone"] = person.telephone()
        user["location"] = { "type": "Point", "coordinates" : [address.longitude(), address.latitude()]}
        user["language"] = person.language()
        if self._max_friends > 0:
            user["friends"] = self.make_friends()
        sample_size = random.randint(0,5)
        user["interests"] = random.sample(User.interests, sample_size)
        return user

    def make_users(self):
        for i in range(self._user_id_start, self._user_id_end):
            yield self.make_one_user(i)


class Sessions:

    def __init__(self, user:dict, total:int):

        self._user_id = user["user_id"]
        self._start_time = user["registered"]
        self._total = total

    @property
    def total(self):
        return self._total

    @property
    def total_documents(self):
        return self._total * 2

    @staticmethod
    def future_random_time(now, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, basis=1):
        return now + timedelta(days=random.randint(basis, basis+days),
                               hours=random.randint(basis, basis+hours),
                               minutes=random.randint(basis, basis+minutes),
                               milliseconds=random.randint(basis, basis+milliseconds))

    def make_session(self, start_ts):

        login_ts = self.future_random_time( now=start_ts, minutes=180, seconds=59, milliseconds=999)
        logout_ts = self.future_random_time(now=login_ts, minutes=180, seconds=59, milliseconds=999)

        login_session = {"user_id": self._user_id,
                         "login": login_ts}

        logout_session = {"user_id": self._user_id,
                          "logout": logout_ts }

        return login_session, logout_session

    def make_sessions(self):
        start = self._start_time
        for i in range(self._total):
            s1,s2 = self.make_session(start)
            start = s2["logout"]
            yield s1,s2


