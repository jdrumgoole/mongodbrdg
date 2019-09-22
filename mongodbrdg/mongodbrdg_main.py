import pymongo
import argparse
import pprint
from datetime import datetime
import sys
from mongodbrdg.randomdata import User, Sessions
from mongodbrdg.inserter import Inserter
from mongodbrdg.version import __VERSION__
import random


def main():
    parser = argparse.ArgumentParser(prog="mongodbrdg",
                                     description=f"mongodbrdg {__VERSION__}. "
                                                 f"Generate random JSON data for MongoDB (requires python 3.6).")
    parser.add_argument("--mongodb", default="mongodb://localhost:27017", help="MongoDB host: [default: %(default)s]")
    parser.add_argument("--database", default="USERS", help="MongoDB database name: [default: %(default)s]")
    parser.add_argument("--collection", default="profiles",
                        help="Default collection for random data:[default: %(default)s]")
    parser.add_argument("--count", default=10, type=int, help="How many docs to create: [default: %(default)s]")
    parser.add_argument("--batchsize", default=1000, type=int,
                        help="How many docs to insert per batch: [default: %(default)s]")
    parser.add_argument("-locale", default="en", help="Locale to use for data: [default: %(default)s]")
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

    args = parser.parse_args()

    client = pymongo.MongoClient(args.mongodb)

    db = client[args.database]
    user_collection = db[args.collection]
    user_inserter = Inserter(user_collection, 1000)

    if args.session != "none" :
        session_collection = db[args.sessioncollection]
        session_inserter = Inserter(session_collection, 1000)

    if args.drop:
        print(f"Dropping collection: '{db.name}.{user_collection.name}'")
        db.drop_collection(args.collection)
        if args.sessions != "none" :
            print(f"Dropping collection: '{db.name}.{session_collection.name}'")
            db.drop_collection(args.sessioncollection)

    user = User(locale=args.locale, seed=args.seed)

    try:
        user_doc_count: int = 0
        session_doc_count: int = 0
        start = datetime.utcnow()
        for i in range(args.count):
            clone = user.make_user()
            user_doc_count = user_doc_count + 1
            user_inserter.insert(clone)
            if args.report:
                pprint.pprint(clone)
            if args.session != "none":
                if args.session == "random":
                    session_count = random.randint(0, args.sessioncount)
                else:
                    session_count = args.sessioncount

                sessions = Sessions(clone["user_id"], clone["registered"])
                for login, logout in sessions.make_sessions(session_count):
                    session_inserter.insert(login)
                    if args.report:
                        pprint.pprint(login)
                    session_inserter.insert(logout)
                    if args.report:
                        pprint.pprint(logout)
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
        

