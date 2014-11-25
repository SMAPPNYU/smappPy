"""
Module for building up collection of fully-populated twitter User objects
and storing to DB.
"""

import time
import random
import argparse

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime, timedelta

from smappPy.tweepy_pool import APIPool
from smappPy.date import mongodate_to_datetime
from smappPy.tweepy_error_handling import call_with_error_handling

CAPACITY_WAIT = 30

def populate_random_user_collection(api, collection, users):
    """
    Populates a collection (Pymongo collection object, fully connected and authenticated)
    with user data from the twitter REST API endpoint /users/show (removes 'status' - user's
    most recent tweet).
    Parameters:
        api         - Tweepy API object, fully authenticated 
        collection  - Pymongo collection object, fully connected and authenticated
        users       - Iterable of twitter user IDs to populate
    """

    # Make unique index on user ID field, and normal index on random_number field (for sampling)
    # And an index on updated_timestamp, to support sorting by that field
    collection.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)
    collection.ensure_index("random_number", name="index_random", background=True)
    collection.ensure_index("updated_timestamp", name="index_updated", background=True)

    # Take time for most-recent user status for inclusion criteria
    last_status_limit = datetime.now() - timedelta(days=180)
    
    total_considered = 0
    users_found = 0
    users_nonenglish = 0
    users_nostatus = 0
    users_statusnonenglish = 0
    users_recentstatusold = 0

    while users_found < users_desired:
        
        print "Found {0} users of {1}".format(users_found, users_desired)

        # Generate 100 random IDs, attempt user lookup on all, iterate over results
        random_user_ids = [random.randrange(USERID_FIRST, USERID_LAST) for i in range(100)]
        user_list, return_code = call_with_error_handling(api.lookup_users, user_ids=random_user_ids)

        if return_code == 130:
            print ".. Twitter over capacity. Sleeping {0} seconds".format(CAPACITY_WAIT)
            time.sleep(CAPACITY_WAIT)
            continue
        elif return_code != 0:
            print ".. Error {0}. Continuing".format(return_code)
            continue

        total_considered += 100

        for user in user_list:
            # Filter criteria
            if user == None:
                print ".. No user results for id"
                continue
            elif user._json["lang"] != "en":
                print ".. User {0}: language not English".format(user.id)
                users_nonenglish +=1
                continue
            elif "status" not in user._json:
                print ".. User {0}: no status object in user data".format(user.id)
                users_nostatus +=1
                continue
            elif user._json["status"] == None or user._json["status"] == {}:
                print ".. User {0}: no most-recent status object".format(user.id)
                users_nostatus += 1
                continue
            elif "lang" in user._json["status"] and user._json["status"]["lang"] != "en":
                print ".. User {0}: most recent status not in English".format(user.id)
                users_statusnonenglish += 1
                continue
            elif mongodate_to_datetime(user._json["status"]["created_at"]) < last_status_limit:
                print ".. User {0}: most recent status too old".format(user.id)
                users_recentstatusold += 1
                continue

            # Add fields to user raw data, and add to collection
            raw_user = user._json
            raw_user["frequency"] = 0
            raw_user["latest_tweet_id"] = None
            raw_user["updated_timestamp"] = datetime.now()
            raw_user["created_at_timestamp"] = mongodate_to_datetime(raw_user["created_at"])
            raw_user["random_number"] = random.random()
            del(raw_user["status"])

            try:
                collection.insert(raw_user)
            except DuplicateKeyError as e:
                print ".. User {0}: already exists in DB. Skipping".format(user.id)
                continue
            users_found += 1
    # Report
    print "Total user IDs considered: {0}".format(total_considered)
    print "Users found: {0}".format(users_found)
    print "User language not English: {0}".format(users_nonenglish)
    print "User has no status: {0}".format(users_nostatus)
    print "User's status not English: {0}".format(users_statusnonenglish)
    print "User's status too old: {0}".format(users_recentstatusold)
    print "Complete"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create random user list")
    parser.add_argument("-s", "--host", action="store", dest="host", default="localhost",
        help="Database server host (default localhost)")
    parser.add_argument("-p", "--port", action="store", type=int, dest="port", default=27017,
        help="Database server port (default 27017)")
    parser.add_argument("-u", "--user", action="store", dest="user", default=None,
        help="Database username (default None, ok when username + pass not required")
    parser.add_argument("-w", "--password", action="store", dest="password", default=None, 
        help="Database password (default None, ok when username + pass not required")
    parser.add_argument("-d", "--db", action="store", dest="database", required=True,
        help="Database to store data in")
    parser.add_argument("-c", "--collection", action="store", dest="collection", required=True,
        help="Collection to store data in")
    parser.add_argument("-o", "--oauthsfile", action="store", dest="oauthsfile", required=True,
        help="JSON file w/ LIST of OAuth keys (consumer, consumer secret, access token, access secret)")
    parser.add_argument("-n", "--number", action="store", type=int, dest="num_users", default=100,
        help="Number of users to gather information on")
    args = parser.parse_args()

    # Create Pymongo database client and connection
    mc = MongoClient(args.host, args.port)
    db = mc[args.database]
    if args.user and args.password:
        if not db.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(user, database))
    col = db[args.collection]

    # Create smappPy APIPool
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Populate DB with user data
    populate_random_user_collection(api, col, args.num_users)