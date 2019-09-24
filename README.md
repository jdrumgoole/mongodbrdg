# mongodbrdg - The MongoDB Random Data Generator
Data generator for generating repeatable random data suitable for use in 
MongoDB databases. The data is designed to be random but self consistent. So 
user IDs increase consistently, session docs for login and logout are correctly
ordered and  sequence of login and logout events are also temporarily ordered.

We also ensure that session events happen only after the registered date for
the user. 

We generate one collection by default `USERS/profiles`. Users can generate
a second collection by specifying the `--session` argument. The sessions 
collection is called `USERs.sessions`.

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
                  [--collection COLLECTION] [--idstart IDSTART]
                  [--idend IDEND] [--maxfriends MAXFRIENDS] [--seed SEED]
                  [--drop] [--report] [--session {none,random,count}]
                  [--sessioncount SESSIONCOUNT]
                  [--sessioncollection SESSIONCOLLECTION]
                  [--bucketsize BUCKETSIZE] [--stats] [-locale LOCALE]
                  [--batchsize BATCHSIZE]

mongodbrdg 0.4.5. Generate random JSON data for MongoDB (requires python 3.6).

optional arguments:
  -h, --help            show this help message and exit
  --mongodb MONGODB     MongoDB host: [default: mongodb://localhost:27017]
  --database DATABASE   MongoDB database name: [default: USERS]
  --collection COLLECTION
                        Default collection for random data:[default: profiles]
  --idstart IDSTART     The starting value for a user_id range [default: 0]
  --idend IDEND         The end value for a user_id range: [default: 10]
  --maxfriends MAXFRIENDS
                        Specify max number of friend to include in profile
                        [default: 0]
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
  -locale LOCALE        Locale to use for data: [default: en]
  --batchsize BATCHSIZE
                        How many docs to insert per batch: [default: 1000]
$```

# Example Data
The random data that is random but looks real. We use the python [mimesis](https://mimesis.readthedocs.io/) package
for this purpose. There are two separate collections that can be created. The
first is the `profiles` collection which contains example user records. A typical
example document is:

```json
{
  "first_name": "Donnetta",
  "last_name": "Page",
  "gender": "FEMALE",
  "company": "Syntel",
  "email": "Donnetta.Page@syntel.rio",
  "registered": "2010-06-09 11:06:05.882643",
  "user_id": 0,
  "country": "United States",
  "city": "Hayward",
  "phone": "1-171-738-1641",
  "location": {
    "type": "Point",
    "coordinates": [
      164.393576,
      59.535072
    ]
  },
  "language": "Dari",
  "interests": [
    "Reading",
    "politics"
  ]
}
```

The second is the the `sessions` document.
If the user asks for sessions to be generated the we will generate a seperate
collection keyed by the `user_id` and generate a collection of session
documents.

Session documents look like this:
```json
{
  "user_id": 0,
  "login": "2021-07-02 22:30:28.790370"
}

{
  "user_id": 0,
  "logout": "2021-07-04 00:15:29.543370"
}
```
They always come in matched pairs. A `login` document and a `logout` document. These
docs are keyed by the `user_id` field which always matches to a valid profile
doc.

# Example Usage

Some simple examples of the program in action.
## Create one random doc:
The parameter `--idstart` defaults to zero so this generates a python
[range](https://docs.python.org/3/library/functions.html#func-range) of
0..1 which creates one document.

```shell script
$ mongodbrdg --idend 1
Inserted 1 user docs into USERS.profiles
$
```
## Create a doc and output it
We use the `--report` object to spit out the JSON to stdout. Note that 
although we generate [datetime](https://docs.python.org/3/library/datetime.html) 
objects internally for insertion we convert these to a string representation 
for output to JSON.

```shell script
$ mongodbrdg --idend 1 --report
{
  "first_name": "Patrick",
  "last_name": "David",
  "gender": "MALE",
  "company": "Danaher",
  "email": "Patrick.David@danaher.info",
  "registered": "2034-07-08 12:06:05.728825",
  "user_id": 0,
  "country": "United States",
  "city": "Yucca Valley",
  "phone": "(065) 868-4054",
  "location": {
    "type": "Point",
    "coordinates": [
      -42.659858,
      -2.631433
    ]
  },
  "language": "Malagasy",
  "interests": []
}
Inserted 1 user docs into USERS.profiles
```

## Create many docs
```shell script
$ mongodbrdg --idend 1000
Inserted 1000 user docs into USERS.profiles
$
```

## Create the same data set every time

Use the `--seed` option to specify a random integer seed. Using the same 
seed ensures that the identical set of random data will be generated
every time.


```shell script
 mongodbrdg --idend 1 --report  --seed 123
{
  "first_name": "Billy",
  "last_name": "Evans",
  "gender": "MALE",
  "company": "Antec",
  "email": "Billy.Evans@antec.lt",
  "registered": "2018-05-03 13:17:06.879234",
  "user_id": 0,
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
    "Darts",
    "Golf",
    "politics",
    "Board gaming",
    "Football"
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

You can specify the following arguments to `--session`:

 * `count` : generate a specific number of sessions per user
 * `random` : generate a random number of sessions between 0 and `--sessioncount`
 * `none` (default) : Do not generate session data
 
```shell script
$ mongodbrdg --idend 1 --report  --session count --sessioncount 1
{
  "first_name": "Jetta",
  "last_name": "Cline",
  "gender": "FEMALE",
  "company": "Integra Design",
  "email": "Jetta.Cline@integradesign.aero",
  "registered": "2029-05-09 19:40:34.866333",
  "user_id": 0,
  "country": "United States",
  "city": "Topeka",
  "phone": "(724) 108-6398",
  "location": {
    "type": "Point",
    "coordinates": [
      -154.636317,
      34.894447
    ]
  },
  "language": "Malayalam",
  "interests": [
    "Football",
    "skydiving",
    "Running",
    "politics",
    "Triathlon"
  ]
}
{
  "user_id": 0,
  "login": "2029-05-10 23:28:34.980333"
}
{
  "user_id": 0,
  "logout": "2029-05-12 01:36:35.248333"
}
Inserted 1 user docs into USERS.profiles
Inserted 2 session docs into USERS.sessions
$
```

## Adding Friends to a user

For data requiring a graph structure we can add a friends field to the profile
using the `--maxfriends` field. The default for `--maxfriends` field is 0. 
When the value is zero the field is omitted. For any value greater than zero we
generate 0..`maxfriends` friends for each user. The friends are selected at
random from `--idstart` to `--idend`.

```shell script
$ mongodbrdg --idend 10 --maxfriends 2 --report
{
  "first_name": "Lavona",
  "last_name": "Rodriquez",
  "gender": "FEMALE",
  "company": "Atari",
  "email": "Lavona.Rodriquez@atari.ua",
  "registered": "2005-08-10 22:02:45.687955",
  "user_id": 0,
  "country": "United States",
  "city": "Watsonville",
  "phone": "1-407-350-4386",
  "location": {
    "type": "Point",
    "coordinates": [
      -26.850068,
      -56.593144
    ]
  },
  "language": "Japanese",
  "friends": [
    1,
    2
  ],
  "interests": [
    "Triathlon"
  ]
}
...

  "first_name": "Enrique",
  "last_name": "Dennis",
  "gender": "MALE",
  "company": "ABX Air",
  "email": "Enrique.Dennis@abxair.consulting",
  "registered": "2019-02-17 00:09:41.859429",
  "user_id": 9,
  "country": "United States",
  "city": "Hemet",
  "phone": "159-721-4912",
  "location": {
    "type": "Point",
    "coordinates": [
      -32.912016,
      -11.078288
    ]
  },
  "language": "Tsonga",
  "friends": [
    1,
    7
  ],
  "interests": [
    "Running",
    "Darts"
  ]
}
Inserted 10 user docs into USERS.profiles
```
