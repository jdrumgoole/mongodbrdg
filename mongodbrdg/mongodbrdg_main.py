import pymongo
import argparse
import pprint
from datetime import datetime
import sys
from .randomuser import RandomUser, RandomSessions

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--mongodb", default="mongodb://localhost:27017", help="MongoDB host: [default: %(default)s]")
    parser.add_argument("--database", default="USERS",help="MongoDB database name: [default: %(default)s]")
    parser.add_argument("--collection", default="profiles", help="Default collection for random data:[default: %(default)s]")
    parser.add_argument("--count", default=10, type=int, help="How many docs to create: [default: %(default)s]")
    parser.add_argument("--batchsize", default=1000, type=int, help="How many docs to insert per batch: [default: %(default)s]")
    parser.add_argument("-locale", default="en", help="Locale to use for data: [default: %(default)s]")
    parser.add_argument("--seed", type=int, help="Use this seed value to ensure you always get the same data")
    parser.add_argument("--drop", default=False, action="store_true", help="Drop data before creating a new set [default: %(default)s]")
    parser.add_argument("--report", default=False, action="store_true", help="send all generated JSON to the screen [default: %(default)s]" )
    parser.add_argument("--sessions", default=None, type=int, help="0 to generate a random number of sessions, or a number for a specific number")
    parser.add_argument("--sessioncollection", default="sessions", help="Name of sessions collection: [default: %(default)s]")
    args = parser.parse_args()

    client = pymongo.MongoClient(args.mongodb)

    db = client[args.database]
    users_collection =db[args.collection]
    sessions_collection = db[args.sessionscollection]
    batch = []

    if args.drop:
        print(f"Dropping collection: {users_collection.name}")
        db.drop_collection(args.collection)
    
    user=RandomUser(locale=args.locale, seed=args.seed)


    print("")
    try:
        start=datetime.utcnow()
        for i in range(args.count):
            clone = user.make_user()
            if args.sessions:
                sessions = RandomSessions(clone["user_id"], clone["registered"])
                session_count = random.randint(1, args.sessions)
                for i in sessions.make_sessions()
            #print(f"{i+1}. {user['_id']}")
            if args.report:
                pprint.pprint(clone)
            batch.append(clone)
            if len(batch) % args.batchsize == 0:
                users_collection.insert_many(batch)
                batch = []

        if len(batch) > 0:
            users_collection.insert_many(batch)
            batch = []

        finish = datetime.utcnow()
    except pymongo.errors.BulkWriteError as e:
        print(e.details)
        print(f"Processed {i} docs")
        sys.exit(1)

    elapsed = finish - start
    print("")
    print(f"Inserted {i+1} docs into {db.name}.{users_collection.name}")
    print(f"Elapsed time: {elapsed}")
    elapsed_time = float(elapsed.seconds) + float(elapsed.microseconds)/1000000
    print(f"Elapsed seconds: {elapsed_time}")

    docs_per_second = float(i+1)/elapsed_time
    print(f"Inserted {round(docs_per_second, 0)} docs per second")

    
        

