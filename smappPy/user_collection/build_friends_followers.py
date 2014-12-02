"""
Script containing functions (and a runable Main function) to populate friend and
follower User objects from a collection of seed users.

NOTE: Followers/list and friends/list endpoints have a less rate-limited API
endpoint than do followers/ids and friends/ids (for some reason).
"""

import warnings
import argparse
from random import random
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from smappPy.tweepy_error_handling import call_with_error_handling


def populate_friends(api, user_id, seed_collection, friend_collection, sample=1.0):
    """
    From a seed collection of User documents (any doc with an 'id' field representing
    a valid twitter user ID), queries twitter REST API friends/list endpoint for fully
    populated friend user objects for given user, stores them in given friend_collection.
    
    - seed_collection and friend_collection fully connected, authenticated mongo collection
    objects
    - user_id, either from or to be stored in seed_collection
    - api fully authenticated tweepy API object or smappPy tweepyPool object
    - sample is proportion of friends to fetch (a limiter)

    - Adds user objects to friends collection, and also to User's "friend_ids" list. 
    - Updates User's friends_updated timestamp.

    Currently only does "one hop," ie gets only the seed users' friends
    (not the friends' subsequent friends.)

    TODO: Obvs make so it can just take a list of user IDs, not an entire collection of users.

    TODO: Do in slices of 100 userIDs, so can either make sure have a user obj in DB or get from
    twitter if not
    """
    user_obj = seed_collection.find_one({"id": user_id})
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
    
    friends_list, return_code = call_with_error_handling(api.friends, user_id=user_obj["id"])
    if return_code != 0:
        warnings.warn("Friends call received error {0}\n.. Skipping user {1}".format(return_code, user_id))
        return
    
    friend_ids = []
    for friend in friends_list:
        raw_friend = friend._json
        friend_ids.append(raw_friend["id"])

        raw_friend["random_number"] = random()
        raw_friend["updated_timestamp"] = datetime.now()
        raw_friend["tweet_ids"] = None
        raw_friend["tweet_frequency"] = 0
        raw_friend["tweets_updated"] = None
        raw_friend["friend_ids"] = None
        raw_friend["follower_ids"] = None
        raw_friend["friends_updated"] = None
        raw_friend["followers_updated"] = None
        raw_friend["hop"] = 1

        try:
            friend_collection.save(raw_friend)
        except DuplicateKeyError:
            warnings.warn("Friend {0} already in friends collection".format(raw_friend["id"]))

    if user_obj["friend_ids"] == None:
        user_obj["friend_ids"] = []

    for fid in friend_ids:
        if fid not in user_obj["friend_ids"]:
            user_obj["friend_ids"].append(fid)

    try:
        seed_collection.save(user_obj)
    except DuplicateKeyError:
        warnings.warn("Seed user {0} object duplicated in DB".format(user_id))



def populate_followers(api, user_id, seed_collection, follower_collection, sample=1.0):
    """
    See 'populate_friends'. Same, but for followers.
    """
    user_obj = seed_collection.find_one({"id": user_id})
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
    
    followers_list, return_code = call_with_error_handling(api.followers, user_id=user_obj["id"])
    if return_code != 0:
        warnings.warn("Followers call received error {0}\n.. Skipping user {1}".format(return_code, user_id))
        return
    
    follower_ids = []
    for follower in followers_list:
        raw_follower = friend._json
        follower_ids.append(raw_follower["id"])

        raw_follower["random_number"] = random()
        raw_follower["updated_timestamp"] = datetime.now()
        raw_follower["tweet_ids"] = None
        raw_follower["tweet_frequency"] = 0
        raw_follower["tweets_updated"] = None
        raw_follower["friend_ids"] = None
        raw_follower["follower_ids"] = None
        raw_follower["friends_updated"] = None
        raw_follower["followers_updated"] = None
        raw_follower["hop"] = 1

        try:
            follower_collection.save(raw_follower)
        except DuplicateKeyError:
            warnings.warn("Follower {0} already in friends collection".format(raw_follower["id"]))

    if user_obj["follower_ids"] == None:
        user_obj["follower_ids"] = []

    for fid in follower_ids:
        if fid not in user_obj["follower_ids"]:
            user_obj["follower_ids"].append(fid)

    try:
        seed_collection.save(user_obj)
    except DuplicateKeyError:
        warnings.warn("Seed user {0} object duplicated in DB".format(user_id))


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
    parser.add_argument("-sc", "--seed_collection", required=True,
        help="Collection from which seed users are taken")
    parser.add_argument("-frc", "--friends_collection", default=None,
        help="Collection in which to store friends [None]")
    parser.add_argument("-foc", "--followers_collection", default=None,
        help="Collection in which to store followers [None]")
    parser.add_argument("-o", "--oauthsfile", required=True,
        help="Twiiter oauths file. JSON file w/ LIST of app documents")

    args = parser.parse_args()

    # Set up DB connection
    client = MongoClient(args.server, args.port)
    database = client[args.database]
    if args.user and args.password:
        database.authenticate(args.user, args.password)
    seed_collection = database[args.seed_collection]
    friend_collection = database[args.friends_collection]
    follower_collection = database[args.followers_collection]

    # Set up TweepyPool API
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Iterate over all users in seed collection



