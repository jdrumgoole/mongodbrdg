# mongodb_random_data_generator
Data generator for generating repeatable random data suitable for use in MongoDB Python programs.

## Installation

To install use `pip` or `pipenv`. You must be using python 3.6 or greater. 

```shell script
$ pip install mongodbrdg
Collecting mongodbrdg
...
Successfully built mongodbrdg
Installing collected packages: mongodbrdg
Successfully installed mongodbrdg-0.2a1
```

## Running mongodbrdg

`mongodbrdg`  installs on your python path and can be run by invoking
```shell script
$ mongodbrdg
```

It expects to have a [mongod](https://docs.mongodb.com/manual/reference/program/mongod/)
running on the default port (27017). You can point the program at a different
`mongod` and/or cluster by using the `--mongodb` argument.

# Command line arguments
```shell script
$ mongodbrdg -h
usage: mongodbrdg [-h] [--mongodb MONGODB] [--database DATABASE]
                  [--collection COLLECTION] [--count COUNT]
                  [--batchsize BATCHSIZE] [-locale LOCALE] [--seed SEED]
                  [--drop] [--report] [--session {none,random,count}]
                  [--sessioncount SESSIONCOUNT]
                  [--sessioncollection SESSIONCOLLECTION]
                  [--bucketsize BUCKETSIZE] [--stats]

mongodbrdg 0.1a3. Generate random JSON data for MongoDB (requires python 3.6).

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
  --session {none,random,count}
                        Generate a sessions collection [default: none do not
                        generate]
  --sessioncount SESSIONCOUNT
                        Default number of sessions to generate.Gives the
                        random bound for random sessions [default: 5]
  --sessioncollection SESSIONCOLLECTION
                        Name of sessions collection: [default: sessions]
  --bucketsize BUCKETSIZE
                        Bucket size for insert_many [default: 1000]
  --stats               Report time to insert data
```

# Example Data
The random data that is random but looks real. We use the python [mimesis](https://mimesis.readthedocs.io/) package
for this purpose. There are two separate collections that can be created. The
first is the `profiles` collection which contains example user records. A typical
example document is:

```json
{'city': 'Mayfield Heights',
 'company': 'Spectrum Brands',
 'country': 'United States',
 'email': 'Sharee.Velasquez@spectrumbrands.biz',
 'first_name': 'Sharee',
 'gender': 'FEMALE',
 'interests': ['Swimmming',
               'Triathlon',
               'skydiving',
               'Football',
               'Stamp Collecting'],
 'language': 'German',
 'last_name': 'Velasquez',
 'location': {'coordinates': [173.464642, -22.135456], 'type': 'Point'},
 'phone': '1-205-730-1945',
 'registered': datetime.datetime(2021, 7, 14, 9, 32, 0, 850772),
 'user_id': 1000}
```

The second is the the `sessions` document.
If the user asks for sessions to be generated the we will generate a seperate
collection keyed by the `user_id` and generate a collection of session
documents.

Session documents look like this:
```json
{'login': datetime.datetime(2026, 1, 16, 15, 51, 53, 202014), 'user_id': 1000}
{'logout': datetime.datetime(2026, 1, 17, 17, 42, 53, 881014), 'user_id': 1000}
```
They always come in matched pairs. A `login` document and a `logout` document. These
docs are keyed by the `user_id` field which always matches to a valid profile
doc.

# Example Usage

Some simple examples of the program in action.
## Create one random doc:
```shell script
$ mongodbrdg --count 1
Inserted 1 user docs into USERS.profiles
$
```
## Create a doc and output it
We use the `--report` object to spit out the JSON to stdout. 
```shell script
$ mongodbrdg --count 1 --report
{
  "first_name": "Jefferson",
  "last_name": "Lara",
  "gender": "MALE",
  "company": "Briggs & Stratton",
  "email": "Jefferson.Lara@briggs&stratton.int",
  "registered": "2029-04-08 22:40:45.385561",
  "user_id": 1000,
  "country": "United States",
  "city": "Fort Pierce",
  "phone": "592-619-1243",
  "location": {
    "type": "Point",
    "coordinates": [
      87.150856,
      66.17156
    ]
  },
  "language": "Aymara",
  "interests": []
}
Inserted 1 user docs into USERS.profiles
```

## Create many docs
```shell script
$ mongodbrdg --count 100
Inserted 100 user docs into USERS.profiles
$
```

## Create the same data set every time

Use the `--seed` option to specify a random integer seed.

```shell script
$ mongodbrdg --count 1 --report  --seed 123
{
  "first_name": "Bobbye",
  "last_name": "Evans",
  "gender": "FEMALE",
  "company": "Antec",
  "email": "Bobbye.Evans@antec.lt",
  "registered": "2006-05-03 13:17:06.879234",
  "user_id": 1000,
  "country": "United States",
  "city": "Battle Ground",
  "phone": "1-288-353-0157",
  "location": {
    "type": "Point",
    "coordinates": [
      -83.63622,
      48.41215
    ]
  },
  "language": "Dhivehi",
  "interests": [
    "Reading"
  ]
}
Inserted 1 user docs into USERS.profiles
```

## Generate a user record and associated session records

We specify that we want session records with the ``--session count`` arg. This
tells use to generate a specific number of sessions. We then specify the number
of sessions with `--sessioncount`. A single session generates a `login` and a 
`logout` document. For any given session the `logout` session always happens
after the `login` session.

```shell script
{
  "first_name": "Shirley",
  "last_name": "Fuller",
  "gender": "MALE",
  "company": "Sky High Financial Advice",
  "email": "Shirley.Fuller@skyhighfinancialadvice.int",
  "registered": "2032-07-08 19:54:00.639183",
  "user_id": 1000,
  "country": "United States",
  "city": "St. Matthews",
  "phone": "1-036-033-1053",
  "location": {
    "type": "Point",
    "coordinates": [
      12.57423,
      58.401794
    ]
  },
  "language": "Finnish",
  "interests": [
    "Stamp Collecting",
    "Soccer"
  ]
}
{
  "user_id": 1000,
  "login": "2032-07-09 21:39:00.956183"
}
{
  "user_id": 1000,
  "logout": "2032-07-11 00:24:01.159183"
}
Inserted 1 user docs into USERS.profiles
Inserted 2 session docs into USERS.sessions
$
```

