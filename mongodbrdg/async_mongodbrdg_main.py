
import argparse
from datetime import datetime
import sys
import random
import json
from enum import Enum
from typing import List
import asyncio

import pymongo
import pprint
from motor import motor_asyncio

from mongodbrdg.randomdata import User, Sessions
from mongodbrdg.inserter import Inserter
from mongodbrdg.version import __VERSION__


class Format(Enum):
    json = 'json'
    python = 'python'

    def __str__(self):
        return self.value


def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

def print_json(doc, indent=2):
    print(json.dumps(doc, indent=indent, default=date_converter))


def report(doc, f:Format=Format.json, indent=2):
    if f == Format.json:
        print(json.dumps(doc, indent=indent, default=date_converter))
    else:
        pprint.pprint(doc, indent=indent)

class Users:

    def __init__(self,
                 q:asyncio.Queue,
                 locale="en",
                 id_start=0,
                 id_end=10,
                 max_friends=0,
                 start_year=2015,
                 end_year=2019,
                 seed=None,
                 sentinel = None):

        self._q = q
        self._user = User(locale=locale,
                          user_id_start=id_start,
                          user_id_end=id_end,
                          max_friends=max_friends,
                          start_year=start_year,
                          end_year=end_year,
                          seed=seed)
        self._sentinel = sentinel

    async def produce(self):
        for i,doc in enumerate(self._user.make_users(),1):
            await self._q.put(doc)
            # print(f"Put doc {i} on queue")
        await self._q.put(self._sentinel)
        # print("Put sentinel on queue")

    def __call__(self):
        return self.produce()


class Distributor:

    def __init__(self, input_q:asyncio.Queue,
                 output_qs:List[asyncio.Queue],
                 sentinel=None):

        self._input_q = input_q
        self._output_qs = output_qs
        self._sentinel = sentinel

    async def distribute(self):
        while True:
            item = await self._input_q.get()
            # print("Got item")
            for q in self._output_qs:
                await q.put(item)
            if item == self._sentinel:
                # print("distributor got sentinel")
                break

    def __call__(self):
        return self.distribute()

class MongoDBConsumer:

    def __init__(self, q:asyncio.Queue,
                 mongodb_url:str="mongodb://localhost:27017",
                 db_name:str="test",
                 col_name:str="test",
                 buffer_size=1000,
                 sentinel=None):

        self._q = q
        self._url = mongodb_url
        self._client = motor_asyncio.AsyncIOMotorClient(self._url)
        self._db = self._client[db_name]
        self._col = self._db[col_name]
        self._buffer_size = buffer_size
        self._buffer =[]
        self._sentinel = sentinel
        self._count = 0

    async def insert(self, item):
        self._buffer.append(item)
        if len(self._buffer) >= self._buffer_size:
            await self.flush()

    async def flush(self):
            if len(self._buffer) > 0 :
                await self._col.insert_many(self._buffer)
                # print("Flushed items")
                self._buffer = []

    async def consume(self):
        buffer=[]
        while True:
            item = await self._q.get()
            # print("MDB got item")
            if item == self._sentinel:
                # print("MDB got sentinel")
                break
            await self.insert(item)
            self._count = self._count + 1
        await self.flush()

    def __call__(self):
        return self.consume()

    @property
    def count(self):
        return self._count





def main():
    parser = argparse.ArgumentParser(prog="mongodbrdg",
                                     description=f"mongodbrdg {__VERSION__}. "
                                                 f"Generate random JSON data for MongoDB (requires python 3.6).")
    parser.add_argument("--mongodb", default="mongodb://localhost:27017", help="MongoDB host: [default: %(default)s]")
    parser.add_argument("--database", default="USERS", help="MongoDB database name: [default: %(default)s]")
    parser.add_argument("--collection", default="profiles",
                        help="Default collection for random data:[default: %(default)s]")
    parser.add_argument("--idstart", default=0, type=int,
                        help="The starting value for a user_id range [default: %(default)s]")
    parser.add_argument("--idend", default=10, type=int,
                        help="The end value for a user_id range: [default: %(default)s]")
    parser.add_argument("--startyear", type=int, default=2015,
                        help="Starting date range for a query [default: %(default)s]")
    parser.add_argument("--endyear", type=int,default=2019,
                        help="Ending date range for a query [default: %(default)s]")
    parser.add_argument("--maxfriends", default=0, type=int,
                        help="Specify max number of friend to include in profile [default: %(default)s]")
    parser.add_argument("--seed", default=None, type=int, help="Use this seed value to ensure you always get the same data")
    parser.add_argument("--drop", default=False, action="store_true",
                        help="Drop data before creating a new set [default: %(default)s]")
    parser.add_argument("--report", default=False, action="store_true",
                        help="send all generated JSON to the screen [default: %(default)s]")
    parser.add_argument("--session", choices=["none", "random", "count"], default="none",
                        help="Generate a sessions collection [default: %(default)s do not generate] ")
    parser.add_argument("--sessioncount", default=5, type=int,
                        help="Default number of sessions to generate."
                             "Gives the random bound for random sessions [default: %(default)s]")
    parser.add_argument("--sessioncollection", default="sessions",
                        help="Name of sessions collection: [default: %(default)s]")
    parser.add_argument("--bucketsize", type=int, default=1000,
                        help="Bucket size for insert_many [default: %(default)s]")
    parser.add_argument("--stats", default=False, action="store_true",
                        help="Report time to insert data")
    parser.add_argument('--format', type=Format, choices=list(Format), default=Format.json,
                        help="Define output format for --report [default: %(default)s]")
    parser.add_argument("-locale", default="en", help="Locale to use for data: [default: %(default)s]")
    parser.add_argument("--batchsize", default=1000, type=int,
                        help="How many docs to insert per batch: [default: %(default)s]")

    args = parser.parse_args()

    q: asyncio.Queue=asyncio.Queue()
    mdb_q = asyncio.Queue=asyncio.Queue()

    assert args.startyear <= args.endyear

    users = Users(q=q,
                  locale=args.locale,
                  id_start=args.idstart,
                  id_end=args.idend,
                  max_friends=args.maxfriends,
                  start_year=args.startyear,
                  end_year=args.endyear,
                  seed=args.seed)

    distributor = Distributor(input_q=q,
                              output_qs=[mdb_q])

    user_consumer = MongoDBConsumer(q=mdb_q,
                                    mongodb_url=args.mongodb,
                                    db_name=args.database,
                                    col_name=args.collection)


    # if args.session != "none" :
    #     session_collection = db[args.sessioncollection]
    #     session_inserter = Inserter(session_collection, 1000)
    #
    # if args.drop:
    #     print(f"Dropping collection: '{db.name}.{user_collection.name}'")
    #     db.drop_collection(args.collection)
    #     if args.session != "none" :
    #         print(f"Dropping collection: '{db.name}.{session_collection.name}'")
    #         db.drop_collection(args.sessioncollection)


    try:
        session_doc_count: int = 0
        start = datetime.utcnow()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(users(), distributor(), user_consumer()))
        loop.close()
        finish = datetime.utcnow()
    except pymongo.errors.BulkWriteError as e:
        print(e.details)
        print(f"Processed {i} docs")
        sys.exit(1)

    elapsed = finish - start
    print(f"Inserted {user_consumer.count} user docs into {args.database}.{args.collection}")
    # if args.session != "none":
    #     print(f"Inserted {session_doc_count} session docs into {db.name}.{session_collection.name}")

    if args.stats:
        print(f"Elapsed time: {elapsed}")
        elapsed_time = float(elapsed.seconds) + float(elapsed.microseconds) / 1000000
        print(f"Elapsed seconds: {elapsed_time}")

        docs_per_second = float(user_consumer.count) / elapsed_time
        print(f"Inserted {round(docs_per_second, 0)} docs per second")

if __name__ == "__main__":
    main()
        

