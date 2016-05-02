"""
Uploads basic userdocs to DB without calling Twitter API to populate them.
Takes file containing list of IDs

@auth dpb
@date 12/01/2014
"""

import os
import argparse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from smappPy.user_collection.userdocs import ensure_userdoc_indexes, create_userdoc

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
        help="Collection to store user data in")
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
    print "Ensuring collection indexes"
    ensure_userdoc_indexes(collection)

    # Create and save userdocs for all userids
    for uid in user_ids:
        print ".. Processing user {0}".format(uid)
        userdoc = create_userdoc(uid)
        try:
            collection.save(userdoc)
        except DuplicateKeyError as e:
            print ".... Userdoc for user {0} already in DB. Skipping".format(uid)
            continue

    print "Complete"