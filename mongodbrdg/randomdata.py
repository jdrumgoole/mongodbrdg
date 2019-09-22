from datetime import timedelta
from mimesis import Generic
from mimesis.enums import Gender
import random
from datetime import datetime

class User:

    def __init__(self, locale: str = "en", seed: int = None) -> object:

        self._locale = locale
        self._seed = seed
        if self._seed:
            self._generic = Generic(self._locale, self._seed)
        else:
            self._generic = Generic(self._locale)

        self._user_id = 1000

    def make_user(self):

        person = self._generic.person
        address = self._generic.address
        business = self._generic.business
        internet = self._generic.internet
        datetime = self._generic.datetime

        user = {}
        interests = ["Soccer", "Golf", "Football", "Stamp Collecting", "skydiving",
                     "Board gaming", "Darts", "Swimmming", "Triathlon", "Running",
                     "Reading", "politics"]

        gender = random.choice(list(Gender))
        gender_string = str(gender).split(".")[1]
        user["first_name"] = person.name(gender)
        user["last_name"] = person.surname(gender)
        user["gender"] = gender_string
        user["company"] = business.company()
        email_domain = "".join(user['company'].lower().split(" "))
        user["email"] = f"{user['first_name']}.{user['last_name']}@{email_domain}{internet.top_level_domain()}"
        year = random.randint(2000, 2018)
        user["registered"] = datetime.datetime(start=year)
        user["user_id"] = self._user_id
        self._user_id = self._user_id + 1
        user["country"]= address.country()
        user["city"] = address.city()
        user["phone"] = person.telephone()
        user["location"] = { "type": "Point", "coordinates" : [address.longitude(), address.latitude()]}
        user["language"] = person.language()
        sample_size = random.randint(0,5)
        user["interests"] = random.sample(interests, sample_size)
        return user


class Sessions:

    def __init__(self, user_id:int, start_time:datetime):
        self._user_id = user_id
        self._start_time = start_time

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

    def make_sessions(self, count):
        start = self._start_time
        for i in range(count):
            s1,s2 = self.make_session(start)
            start = s2["logout"]
            yield s1,s2


