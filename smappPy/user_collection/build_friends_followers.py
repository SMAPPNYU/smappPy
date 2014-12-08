"""
Script containing functions to populate friend and follower User objects from
a collection of seed users.

@auth dpb
@date 12/01/2014
"""

import argparse
import warnings
from tweepy import Cursor
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from smappPy.tweepy_pool import APIPool
from smappPy.tweepy_error_handling import call_with_error_handling
from smappPy.user_collection.userdocs import ensure_userdoc_indexes, create_userdoc
from smappPy.user_collection.network_edges import create_edge_doc, ensure_edge_indexes


#TODO: def get_friend_ids_sample(api, user_id, user_doc=None, sample=0.1)
#TODO: Gets sample proportion of friends. Takes userdoc: if None, queries
#TODO: rest API for user, get num friends, iterates over cursor until sample
#TODO: number is hit

#TODO: def get_friends(api, user_id)
#TODO: Gets fully-hydrated friend user docs via Tweepy 'friends' method

#TODO: Change all prints and info to logging


def get_friends_ids(api, user_id):
    """
    Given a Tweepy/smappPy TweepyPool api, query twitter's rest API for friends of
    given user_id. Returns IDs only (much faster / more per request).
    Parameters:
        api     - fully authenticated Tweepy api or smappPy TweepyPool api
        user_id - twitter user id
    Returns list of IDs or None (if API call fails)
    """
    user_list, ret_code = call_with_error_handling(list,
        Cursor(api.friends_ids, user_id=user_id).items())

    if ret_code != 0:
        warnings.warn("User {0}: Friends request failed")
    
    # Retun user list from API or None (call_with_error_handling returns None if
    # call fail)
    return user_list

def get_followers_ids(api, user_id):
    """
    Given a Tweepy/smappPy TweepyPool api, query twitter's rest API for followers of
    given user_id. Returns IDs only (much faster / more per request).
    Parameters:
        api     - fully authenticated Tweepy api or smappPy TweepyPool api
        user_id - twitter user id
    Returns list of IDs or None (if API call fails)
    """
    user_list, ret_code = call_with_error_handling(list,
        Cursor(api.followers_ids, user_id=user_id).items())

    if ret_code != 0:
        warnings.warn("User {0}: Followers request failed")
    
    # Retun user list from API or None (call_with_error_handling returns None if
    # call fail)
    return user_list

#TODO: Add friends_sample functionality, depending on get_friend_ids_sample
def populate_friends_from_collection(api, seed_collection, friend_collection, edge_collection=None,
    user_sample=1.0, print_progress_every=1000):
    """
    Populates given 'friends_collection' with local user documents representing the friends
    of each user in given 'seed_collection'.
    Note: populated documents are NOT fully hydrated twitter user objects, just IDs with 
    status fields. 
    'friend_ids' field of seed_collection user docs will also be updated with IDs of friends
    fetched from twitter API.
    Parameters:
        api     - fully authenticated Tweepy api or smappPy TweepyPool api
        seed_collection    - fully authenticated (read/write) mongo collection
        friend_collection  - fully authenticated (read/write) mongo collection
        edge_collection    - [OPTIONAL] collection to store simple edge: {to: ID, from: ID}
        user_sample        - proportion of seed users to fetch friends for
    """
    # Ensure indexes
    ensure_userdoc_indexes(seed_collection)
    ensure_userdoc_indexes(friend_collection)
    if edge_collection:
        ensure_edge_indexes(edge_collection)

    # Sample users (if necessary)
    if user_sample < 1.0:
        seed_count = seed_collection.count()
        users = seed_collection.find(limit=int(seed_count * user_sample))
    else:
        users = seed_collection.find()

    # Progress vars
    user_count = users.count(with_limit_and_skip=True)
    user_it = 1

    # Iterate over users, get friends, save user and friends
    friend_request_failed_for = []
    for user in users:
        if user_it % print_progress_every == 0:
            print ".. Processing user {0} of {1}".format(user_it, user_count)
        user_it += 1

        friend_ids = get_friends_ids(api, user["id"])
        if friend_ids == None:
            friend_request_failed_for.append(user["id"])
            continue

        # Initialize (if necessary) and set user's friend_ids list
        if not user["friend_ids"]:
            user["friend_ids"] = list(set(friend_ids))
        else:
            user["friend_ids"] = list(set(user["friend_ids"] + friend_ids))

        for friend_id in friend_ids:
            # Create and save friend doc to friend collection
            friend_doc = create_userdoc(friend_id)
            try:
                friend_collection.save(friend_doc)
            except DuplicateKeyError:
                #warnings.warn("Friend {0} already in friends collection".format(
                #    friend_id))
                continue

        # Optionally save "edge" document
        if edge_collection:
            for friend_id in friend_ids:
                edge_doc = create_edge_doc(user["id"], friend_id)
                try:
                    edge_collection.save(edge_doc)
                except DuplicateKeyError:
                    warnings.warn("Edge {0} alread in DB, skipping".format(
                        edge_doc))

        # Update user doc's timestamps and save
        user["updated_timestamp"] = datetime.now()
        user["friends_updated"] = datetime.now()
        seed_collection.save(user)

    # Print failure numbers
    print "Failed to find friends for {0} users".format(len(friend_request_failed_for))


#TODO: Add followers_sample functionality, depending on get_followers_ids_sample
def populate_followers_from_collection(api, seed_collection, follower_collection, edge_collection=None,
    user_sample=1.0, print_progress_every=1000):
    """
    See 'populate_friends_from_collection'. Exactly the same, but for followers
    """
    # Ensure indexes
    ensure_userdoc_indexes(seed_collection)
    ensure_userdoc_indexes(follower_collection)
    if edge_collection:
        ensure_edge_indexes(edge_collection)

    # Sample users (if necessary)
    if user_sample < 1.0:
        seed_count = seed_collection.count()
        users = seed_collection.find(limit=int(seed_count * user_sample))
    else:
        users = seed_collection.find()

    # Progress vars
    user_count = users.count(with_limit_and_skip=True)
    user_it = 1

    # Iterate over users, get followers, save user and followers
    follower_request_failed_for = []
    for user in users:
        if user_it % print_progress_every == 0:
            print ".. Processing user {0} of {1}".format(user_it, user_count)
        user_it += 1

        follower_ids = get_followers_ids(api, user["id"])
        if follower_ids == None:
            follower_request_failed_for.append(user["id"])
            continue

        # Initialize (if necessary) and set user's follower_ids list
        if not user["follower_ids"]:
            user["follower_ids"] = list(set(follower_ids))
        else:
            user["follower_ids"] = list(set(user["follower_ids"] + follower_ids))

        for follower_id in follower_ids:
            # Create and save follower doc to follower collection
            follower_doc = create_userdoc(follower_id)
            try:
                follower_collection.save(follower_doc)
            except DuplicateKeyError:
                #warnings.warn("Follower {0} already in followers collection".format(
                #   follower_id))
                continue

        # Optionally save "edge" document
        if edge_collection:
            for follower_id in follower_ids:
                edge_doc = create_edge_doc(follower_id, user["id"])
                try:
                    edge_collection.save(edge_doc)
                except DuplicateKeyError:
                    warnings.warn("Edge {0} alread in DB, skipping".format(
                        edge_doc))

        # Update user doc's timestamps and save
        user["updated_timestamp"] = datetime.now()
        user["followers_updated"] = datetime.now()
        seed_collection.save(user)

    # Print failure numbers
    print "Failed to find followers for {0} users".format(len(friend_request_failed_for))


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
    parser.add_argument("-ec", "--edge_collection", default=None,
        help="Collection in which to store network edges [None]")
    parser.add_argument("-o", "--oauthsfile", required=True,
        help="Twitter oauths file. JSON file w/ LIST of app documents")
    parser.add_argument("-ppe", "--print_progress_every", type=int,
        default=1000, help="Print progress every Nth user [1000]")
    args = parser.parse_args()

    # Set up TweepyPool API
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Set up DB connection
    client = MongoClient(args.server, args.port)
    database = client[args.database]
    if args.user and args.password:
        database.authenticate(args.user, args.password)
    seed_collection = database[args.seed_collection]
    edge_collection = database[args.edge_collection] if args.edge_collection else None

    if args.friends_collection:
        print "Populating Friends from {0}".format(seed_collection)
        friend_collection = database[args.friends_collection]
        populate_friends_from_collection(api, seed_collection, friend_collection, 
            edge_collection=edge_collection, user_sample=1.0,
            print_progress_every=args.print_progress_every)
        print "Friends complete"
    
    if args.followers_collection:
        print "Populating Followers from {0}".format(seed_collection)
        follower_collection = database[args.followers_collection]
        populate_followers_from_collection(api, seed_collection, follower_collection, 
            edge_collection=edge_collection, user_sample=1.0,
            print_progress_every=args.print_progress_every)
        print "Followers complete"





