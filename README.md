# mongodb_random_data_generator
Data generator for generating repeatable random data suitable for use in MongoDB Python programs.
```python
(mongodb_random_data_generator) bash-3.2$ mongodbrdg_-h
usage: mongodbrdg_main.py [-h] [--mongodb MONGODB] [--database DATABASE]
                          [--collection COLLECTION] [--count COUNT]
                          [--batchsize BATCHSIZE] [-locale LOCALE]
                          [--seed SEED] [--drop] [--report]
                          [--sessions SESSIONS]
                          [--sessioncollection SESSIONCOLLECTION]
                          [--bucketsize BUCKETSIZE]

optional arguments:
  -h, --help            show this help message and exit
  --mongodb MONGODB     MongoDB host: [default: mongodb://localhost:27017]
  --database DATABASE   MongoDB database name: [default: USERS]
  --collection COLLECTION
                        Default collection for random data:[default: profiles]
  --count COUNT         How many docs to create: [default: 10]
  --batchsize BATCHSIZE
                        How many docs to insert per batch: [default: 1000]
  -locale LOCALE        Locale to use for data: [default: en]
  --seed SEED           Use this seed value to ensure you always get the same
                        data
  --drop                Drop data before creating a new set [default: False]
  --report              send all generated JSON to the screen [default: False]
  --sessions SESSIONS   0 to generate a random number of sessions, or a number
                        for a specific number
  --sessioncollection SESSIONCOLLECTION
                        Name of sessions collection: [default: sessions]
  --bucketsize BUCKETSIZE
                        Bucket size for insert_many [default: 1000]
```
