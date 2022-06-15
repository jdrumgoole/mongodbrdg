import argparse
import pprint
import uuid
import random
from datetime import datetime

import pymongo
from mimesis import Datetime, Finance, Internet

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--host", default="mongodb://localhost:27017", help="mongodb URL for host")
    parser.add_argument("--database", default="COLBY", help="default database [COLBY]")
    parser.add_argument("--collection", default="data", help="default collection [data]")
    parser.add_argument("--drop", default=False, action="store_true", help="Drop the users database")
    parser.add_argument("--seed", default=None, type=int, help="seed for random data generator")
    parser.add_argument("--batchsize", default=1000, type=int, help="Size of batch to insert_many")
    parser.add_argument("--verbose", default=False, action="store_true", help="echo output if on")
    parser.add_argument("--count", default=0, type=int, help="How many records to create, default is 0. "
                                                             "If 0 keep creating records for ever")

    args = parser.parse_args()

    dater = Datetime()
    financer = Finance()
    interner = Internet()

    client = pymongo.MongoClient(host=args.host)
    db = client[args.database]
    rand_collection = db[args.collection]
    insert_list = []
    counter = 0

    if args.drop:
        if args.verbose:
            print(f"Dropping collection: '{args.database}:{args.collection}'")
        db.drop_collection(args.collection)
    '''
    websiteId: GUID uuid.uuid4()
    ipType : domain URL Internet.ip_v4() or hostname(TLDTypes.GTLD)
    createdAt : datetime Datetime.date(start=yr, end=yr)
    companyId : Fake Company name Finance.company()
    visitorId : GUID
    urlVisted : protocol host path query string
    '''
    counter = 0
    start_time = datetime.utcnow()
    while True:
        doc = {
            "websiteId": str(uuid.uuid4()),
            "ipType": interner.ip_v4(),
            "createdAt": dater.datetime(start=2015, end=2020),
            "companyId": financer.company(),
            "visitorId" : str(uuid.uuid4()),
            "urlVisited": interner.uri(query_params_count=random.randint(0, 3)),
        }
        if args.verbose:
            pprint.pprint(doc)

        insert_list.append(doc)

        if len(insert_list) >= args.batchsize:
            rand_collection.insert_many(insert_list)
            insert_list = []
        counter = counter + 1
        if counter >= args.count:
            break

    if len(insert_list) > 0:
        rand_collection.insert_many(insert_list)

    end_time = datetime.utcnow()
    duration = end_time - start_time
    print(f"Inserted {args.count} docs in {args.database}:{args.collection}")
    print(f"Duration: {duration}")





