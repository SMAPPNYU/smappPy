"""
tweet_importer - a simple commandline tool to import json tweet files (plaintext) to a specified
mongodb database and collection

@auth dpb
@date 10/07/2013
"""

import argparse
import warnings
from bson.json_util import loads
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

from smappPy.tweet_util import add_random_to_tweet, add_timestamp_to_tweet
from smappPy.json_util import ConcatJSONDecoder,NonListStreamJsonListLoader


def import_tweets(host, port, user, password, database, collection, infile, transform=True, stream_json=False):
    """
    Loads each line from the given infile into a json object, and directly inserts that to the
    given database and collection. 
    NOTE: On fail, DOES NOT ROLL BACK (must manually remove records if clean necessary)
    """
    print "Importing tweets from '{0}' into {1}:{2}".format(infile, database, collection)

    # Create connection and authenticate
    client = MongoClient(host, int(port))
    dbh = client[database]
    assert dbh.connection == client
    if not dbh.authenticate(user, password):
        raise ConnectionFailure("Mongo DB Authentication for User {0}, DB {1} failed".format(user, database))
    col = dbh[collection]

    # Ensure there is a unique ID index on tweet collection
    print "Ensuring indexes on {0}:{1}".format(database, collection)
    col.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)

    # Read tweets via the Custom json decoder (made for reading streams with multiple tweets)
    print "Importing tweets in {0}".format(infile)
    imported = 0
    skipped = 0
    with open(infile) as inhandle:
        if stream_json:
            tweets = NonListStreamJsonListLoader(infile)
            warnings.warn("Using NonListStreamJsonListLoader (SLOW).")
        else:
            tweets = loads(inhandle.read(), cls=ConcatJSONDecoder)
        for tweet in tweets:
            if "id_str" not in tweet:
                warnings.warn("Data read from file\n\t{0}\nnot a valid tweet".format(tweet))
                continue

            if transform:
                add_random_to_tweet(tweet)
                add_timestamp_to_tweet(tweet)

            try:
                col.insert(tweet, safe=True)
            except DuplicateKeyError as e:
                warnings.warn("Tweet already exists in DB. Skipping..")
                skipped += 1
                continue
            imported += 1
            print "Imported {0}\r".format(imported), 
    
    print "Importing complete. Inserted {0} documents in {1}:{2}, skipped {3}".format(
            imported, database, collection, skipped)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import tweet files to a specifed mongo DB and collection")
    parser.add_argument("-s", "--host", action="store", dest="host", required=True,
        help="Database hostname")
    parser.add_argument("-p", "--port", action="store", dest="port", required=True,
        help="Database port on server")
    parser.add_argument("-u", "--user", action="store", dest="user", required=True,
        help="Database user")
    parser.add_argument("-w", "--password", action="store", dest="password", required=True,
        help="User's database password")
    parser.add_argument("-d", "--database", action="store", dest="db", required=True,
        help="Database name on database server")
    parser.add_argument("-c", "--collection", action="store", dest="collection", required=True,
        help="Collection in database")
    parser.add_argument("-f", "--file", action="store", dest="file", required=True, nargs='*',
        help="File to read input from")
    parser.add_argument("--streamjson", action="store_true", dest="stream_json", default=False,
        help="Use streaming JSON decoder. It is SLOW(!), but works for broken files,\
        where the last json object might be terminated prematurely.")

    args = parser.parse_args()
    for filename in args.file:
        import_tweets(args.host, args.port, args.user, args.password, args.db, args.collection, filename, stream_json=args.stream_json)
