
import argparse
from datetime import datetime
import sys
import random
import json
from enum import Enum
import pymongo
import pprint
from queue import Queue
from mongodbrdg.randomuser import User, Sessions
from mongodbrdg.blockinserter import BlockInserter
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
    parser.add_argument("--stats", default=False, action="store_true",
                        help="Report time to insert data")
    parser.add_argument('--format', type=Format, choices=list(Format), default=Format.json,
                        help="Define output format for --report [default: %(default)s]")
    parser.add_argument("--locale", default="en", help="Locale to use for data: [default: %(default)s]")
    parser.add_argument("--batchsize", default=1000, type=int,
                        help="How many docs to insert per batch: [default: %(default)s]")

    args = parser.parse_args()

    assert args.startyear <= args.endyear

    client = pymongo.MongoClient(args.mongodb)

    db = client[args.database]
    user_collection = db[args.collection]
    user_inserter = BlockInserter(user_collection, args.batchsize)

    if args.session != "none":
        session_collection = db[args.sessioncollection]
        session_inserter = BlockInserter(session_collection, args.batchsize)

    if args.drop:
        print(f"Dropping collection: '{db.name}.{user_collection.name}'")
        db.drop_collection(args.collection)
        if args.session != "none" :
            print(f"Dropping collection: '{db.name}.{session_collection.name}'")
            db.drop_collection(args.sessioncollection)

    user = User(locale=args.locale,
                user_id_start=args.idstart,
                user_id_end=args.idend,
                max_friends=args.maxfriends,
                start_year=args.startyear,
                end_year=args.endyear,
                seed=args.seed)

    try:
        session_doc_count: int = 0
        start = datetime.utcnow()
        for user_doc_count, user in enumerate(user.make_users(),1):
            user_inserter.insert_one(user)
            if args.report:
                report(user, args.format)
            if args.session != "none":
                if args.session == "random":
                    session_count = random.randint(0, args.sessioncount)
                else:
                    session_count = args.sessioncount

                sessions = Sessions(user, args.sessioncount)
                for login, logout in sessions.make_sessions():
                    session_inserter.insert(login)
                    if args.report:
                        report(login, args.format)
                    session_inserter.insert(logout)
                    if args.report:
                        report(logout, args.format)
                    session_doc_count = session_doc_count + 2
                session_inserter.flush()

        user_inserter.flush()
        finish = datetime.utcnow()
    except pymongo.errors.BulkWriteError as e:
        print(e.details)
        print(f"Processed {i} docs")
        sys.exit(1)

    elapsed = finish - start
    print(f"Inserted {user_doc_count} user docs into {db.name}.{user_collection.name}")
    if args.session != "none":
        print(f"Inserted {session_doc_count} session docs into {db.name}.{session_collection.name}")

    if args.stats:
        print(f"Elapsed time: {elapsed}")
        elapsed_time = float(elapsed.seconds) + float(elapsed.microseconds) / 1000000
        print(f"Elapsed seconds: {elapsed_time}")

        docs_per_second = float(user_doc_count + session_doc_count) / elapsed_time
        print(f"Inserted {round(docs_per_second, 0)} docs per second")


if __name__ == "__main__":
    main()
        

