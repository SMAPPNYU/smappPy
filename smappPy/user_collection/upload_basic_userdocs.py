"""
Uploads basic userdocs (in accordance with build_user_collection) to DB without having to
call Twitter API to populate them.
"""

import os
import argparse
from random import random
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", default="smapp.politics.fas.nyu.edu",
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
    parser.add_argument("-uf", "--users_file", required=True,
        help="File containing line-separated list of Twitter User IDs")
    args = parser.parse_args()
    args.users_file = os.path.abspath(os.path.expanduser(args.users_file))

    # Set up DB connection
    client = MongoClient(args.server, args.port)
    database = client[args.database]
    if args.user and args.password:
        database.authenticate(args.user, args.password)
    collection = database[args.collection]

    # Get user list
    user_ids = []
    with open(args.users_file, "r") as handle:
        for line in handle:
            user_ids.append(line.strip())
    user_ids = list(set(user_ids))
    print "Uploading {0} IDs from {1}".format(len(user_ids), args.users_file)

    # Ensure indexes on user collection
    collection.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)
    collection.ensure_index("random_number", name="index_random", background=True)
    collection.ensure_index("updated_timestamp", name="index_updated", background=True)

    for uid in user_ids:
        print ".. Processing user {0}".format(uid)

        user_obj = collection.find_one({"id": int(uid)})
        if not user_obj:
            user_obj = {}

        user_obj["id"] = int(uid)
        user_obj["random_number"] = random()
        user_obj["updated_timestamp"] = None
        user_obj["tweet_ids"] = None
        user_obj["tweet_frequency"] = 0
        user_obj["tweets_updated"] = None
        user_obj["friend_ids"] = None
        user_obj["follower_ids"] = None
        user_obj["friends_updated"] = None
        user_obj["followers_updated"] = None
        if "status" in user_obj:
            del(user_obj["status"])
        try:
            collection.save(user_obj)
        except DuplicateKeyError as e:
            print ".... Userdoc for user {0} already in DB. Skipping".format(uid)
            continue
    
    print "Complete"


                