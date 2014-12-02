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

from smappPy.iter_util import grouper
from smappPy.tweepy_pool import APIPool
from smappPy.date import mongodate_to_datetime
from smappPy.tweepy_error_handling import call_with_error_handling

CAPACITY_WAIT = 30
PRINT_PROGRESS_EVERY = 10000

def populate_user_collection(api, collection, user_ids, num_passes=3, not_found_file=None):
    """
    Populates a collection (Pymongo collection object, fully connected and authenticated)
    with user data from the twitter REST API endpoint /users/show (removes 'status' - user's
    most recent tweet).
    Parameters:
        api         - Tweepy or smappPy TweepyPool API object, fully authenticated 
        collection  - Pymongo collection object, fully connected and authenticated
        users       - Iterable of twitter user IDs to populate. Will pull totally into memory
        num_passes  - Number of retries on UIDs failing to come in the first time
        not_found_file - Filename to store all user IDs not found, line separated. If None, no output
    """

    # Make unique index on user ID field, and normal index on random_number field (for sampling)
    # And an index on updated_timestamp, to support sorting by that field
    collection.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)
    collection.ensure_index("random_number", name="index_random", background=True)
    collection.ensure_index("updated_timestamp", name="index_updated", background=True)

    users_not_found = list(set([str(i) for i in user_ids]))
    passnum = 0
    
    while len(users_not_found) > 0 and num_passes > passnum:

        print "Pass {0}, attempting to find {1} users".format(passnum, len(users_not_found))

        users_found_this_pass = []
        for user_group in grouper(100, users_not_found, pad=False):
            user_group = list(user_group)
            user_list, return_code = call_with_error_handling(api.lookup_users, user_ids=user_group)

            if return_code == 130:
                print ".. Twitter over capacity. Sleeping {0} seconds".format(CAPACITY_WAIT)
                time.sleep(CAPACITY_WAIT)
                continue
            elif return_code != 0:
                print ".. Error {0}. Continuing".format(return_code)
                continue

            for user in user_list:
                if not user or not user._json:
                    continue
                users_found_this_pass.append(str(user.id))

                # Add fields to user raw data, and add to collection
                raw_user = user._json
                raw_user["tweet_frequency"] = 0
                raw_user["updated_timestamp"] = datetime.now()
                raw_user["created_at_timestamp"] = mongodate_to_datetime(raw_user["created_at"])
                raw_user["random_number"] = random.random()
                raw_user["friend_ids"] = None
                raw_user["follower_ids"] = None
                raw_user["friends_updated"] = None
                raw_user["followers_updated"] = None
                raw_user["tweet_ids"] = None
                raw_user["tweets_updated"] = None
                del(raw_user["status"])

                try:
                    collection.save(raw_user)
                except DuplicateKeyError as e:
                    print ".. User {0}: already exists in DB. Skipping".format(user.id)
                    continue

        # Remove found users from users not found list
        users_not_found = list(set(users_not_found) - set(users_found_this_pass))
        passnum += 1

    # Report and finish
    print "Total users not found: {0}".format(len(users_not_found))
    if not_found_file and len(users_not_found) > 0:
        print "Writing IDs not found to file: {0}".format(not_found_file)
        with open(not_found_file, "w") as handle:
            for uid in users_not_found:
                handle.write("{0}\n".format(uid))

    print "Complete"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--host", default="smapp.politics.fas.nyu.edu",
        help="Database server host [smapp.politics.fas.nyu.edu]")
    parser.add_argument("-p", "--port", type=int, default=27011,
        help="Database server port [27011]")
    parser.add_argument("-u", "--user", dest="user", default="smapp_readWrite",
        help="Database username [smapp_readWrite]")
    parser.add_argument("-w", "--password", default=None,
        help="Database password [None]")
    parser.add_argument("-d", "--database", required=True,
        help="Database to store data in")
    parser.add_argument("-c", "--collection", required=True,
        help="Collection to store data in")
    parser.add_argument("-o", "--oauthsfile", required=True,
        help="JSON file w/ LIST of OAuth keys")
    parser.add_argument("-uf", "--users_file", required=True,
        help="File containing line-separated list of Twitter User IDs")
    parser.add_argument("-np", "--num_passes", type=int, default=3,
        help="Number passes over user collection to make before giving up [3]")
    parser.add_argument("-of", "--out_file", default=None,
        help="Optional outfile to store IDs in given list not retrievable [None]")

    args = parser.parse_args()

    # Create Pymongo database client and connection
    mc = MongoClient(args.host, args.port)
    db = mc[args.database]
    if args.user and args.password:
        if not db.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(
                    args.user, args.database))
    col = db[args.collection]

    # Create smappPy APIPool
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Get userids list
    user_ids = []
    with open(args.users_file, "r") as handle:
        for line in handle:
            user_ids.append(line.strip())
    print "MAIN: {0} userids parsed from {1}".format(len(user_ids), args.users_file)

    # Populate DB with user data
    populate_user_collection(api, col, user_ids, args.num_passes, args.out_file)





