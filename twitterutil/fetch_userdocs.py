"""
(In contrast to upload_userdocs): From a seed file of user IDs,
get userdocs from Twitter REST API and store in collection

@auth dpb
@date 12/01/2014
"""

import argparse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from smappPy.tweepy_pool import APIPool
from smappPy.user_collection import build_user_collection

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
        help="Collection to store user data in")
    parser.add_argument("-o", "--oauthsfile", required=True,
        help="JSON file w/ LIST of OAuth keys")
    parser.add_argument("-uf", "--users_file", required=True,
        help="File containing line-separated list of Twitter User IDs")
    parser.add_argument("-np", "--num_passes", type=int, default=2,
        help="Number passes over user collection to make before giving up [2]")
    parser.add_argument("-of", "--out_file", default=None,
        help="Optional outfile to store IDs in given list not retrievable [None]")
    args = parser.parse_args()

    # Create Pymongo database client and connection
    client = MongoClient(args.host, args.port)
    database = client[args.database]
    if args.user and args.password:
        if not database.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(
                    args.user, args.database))
    collection = database[args.collection]

    # Create smappPy APIPool
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Get userids list
    user_ids = []
    with open(args.users_file, "r") as handle:
        for line in handle:
            user_ids.append(line.strip())
    user_ids = list(set(user_ids))
    print "{0} userids parsed from {1}".format(len(user_ids), args.users_file)

    # Populate DB with user data
    build_user_collection.populate_user_collection_from_ids(api,
                                                            collection,
                                                            user_ids,
                                                            args.num_passes,
                                                            args.out_file)
    print "Complete"