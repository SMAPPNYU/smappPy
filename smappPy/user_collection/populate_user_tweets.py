"""
Functions and runability to find and fetch tweets of users represented by a
user collection.

@auth dpb
@date 12/04/2014
"""

import time
import tweepy
import random
import argparse

from pymongo import MongoClient
from datetime import datetime, timedelta
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure, CursorNotFound

from smappPy.oauth import tweepy_auth
from smappPy.tweepy_pool import APIPool
from smappPy.collection_util import create_tweet_indexes
from smappPy.tweepy_error_handling import call_with_error_handling
from smappPy.tweet_util import add_random_to_tweet, add_timestamp_to_tweet

over_capacity_wait = 5

def populate_user_tweets(api, user_collection, tweet_collection, tweets_per_user, ensure_indexes=True):
    """
    Iterates through user_collection, querying Twitter API for last 'tweets_per_user'
    tweets. Considers last tweet fetched for each user. Updates user access time and last
    tweet fetched. Calculates and stores user tweet frequency.
    """
    if ensure_indexes:
        print "Ensuring indexes on tweet collection..."
        create_tweet_indexes(tweet_collection)

    #TODO: This sorted find takes a long time on a non-indexed field
    for user in user_collection.find(timeout=False).sort("tweets_updated", ASCENDING):
        print "Considering user {0}".format(user["id"]),

        if user["latest_tweet_id"]:
            cursor = tweepy.Cursor(api.user_timeline, 
                                   user_id=user["id"], 
                                   since_id=user["latest_tweet_id"], 
                                   include_rts=True)
        else:
            cursor = tweepy.Cursor(api.user_timeline, 
                                   user_id=user["id"], 
                                   include_rts=True)

        # While return is error, keep trying to get tweets depending on error type.
        # If error not well-understood, move on to next user
        return_code = -1
        while return_code != 0:
            tweets, return_code = call_with_error_handling(list, cursor.items(tweets_per_user))

            # Twitter over capacity
            if return_code == 130:
                print ".. Over Cap. Sleeping for {0} seconds".format(over_capacity_wait)
                time.sleep(over_capacity_wait)
            # User no longer exists. Move on
            elif return_code == 34:
                print ".. User {0} no longer exists, skipping".format(user["id"])
                break
            elif return_code != 0:
                print ".. Error {0} for user {1}, skipping".format(return_code, user["id"])
                break

        # Do a final check of tweet population. If None, there was an error that waiting
        # and retrying could not fix. If tweets is merely an empty list, still want to update
        # user's 'updated_timestamp' field.
        if tweets == None:
            continue

        # Reverse tweets when storing (given order is newest to oldest)
        saved_count = 0
        for tweet in tweets[::-1]:
            saved_count += save_tweet(tweet_collection, tweet)

        # Calculate frequency
        if len(tweets) < 2:
            frequency = 0
        else:
            first_tweet_date = tweets[-1].created_at
            last_tweet_date = tweets[0].created_at
            frequency = len(tweets) / float((last_tweet_date - first_tweet_date).days or 1)

        latest_tweet_id = tweets[0].id if tweets else None
        update_user(user_collection, user, latest_tweet_id, frequency)
        print ".. {0} tweets found, {1} saved".format(len(tweets), saved_count)

def save_tweet(tweet_collection, tweet):
    """
    Saves a tweet to mongo collection, adds random number for sampling. Returns number
    of tweets saved (1 or 0)
    """
    json_tweet = tweet._json
    add_random_to_tweet(json_tweet)
    add_timestamp_to_tweet(json_tweet)
    try:
        tweet_collection.save(json_tweet)
    except DuplicateKeyError:
        return 0
    return 1

def update_user(user_collection, user, latest_tweet_id, frequency):
    """
    Updates a user's 'latest_tweet_id' and 'updated_timestamp'
    """
    user["updated_timestamp"] = datetime.now()
    user["tweets_updated"] = datetime.now()
    
    # Frequency is a compound average of frequencies
    if "tweet_frequency" in user and user["tweet_frequency"]:
        user["tweet_frequency"] = (user["tweet_frequency"] + frequency) / 2
    else:
        user["tweet_frequency"] = frequency

    if latest_tweet_id:
        user["latest_tweet_id"] = latest_tweet_id

    try:
        user_collection.save(user)
    except Error as e:
        print ".. Couldn't save user: {0}".format(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate random user tweets")
    parser.add_argument("-s", "--server", default="smapp.politics.fas.nyu.edu",
        help="Database server host [smapp.politics.fas.nyu.edu]")
    parser.add_argument("-p", "--port", type=int, default=27011,
        help="Database server port [27011]")
    parser.add_argument("-u", "--user", default=None,
        help="Database username [None - no DB auth required]")
    parser.add_argument("-w", "--password", default=None, 
        help="Database password [None - no DB auth required]")
    parser.add_argument("-d", "--database", required=True,
        help="Database containing user and tweet collections")
    parser.add_argument("-uc", "--user_collection", required=True,
        help="Collection of user data to iterate over")
    parser.add_argument("-tc", "--tweet_collection", required=True,
        help="Collection to hold user tweets")
    parser.add_argument("-a", "--oauthsfile", required=True,
        help="JSON file w/ LIST of Twitter OAuth keys")
    parser.add_argument("-n", "--num_tweets", type=int, default=100,
        help="Number of tweets per user to store [100]")
    parser.add_argument("-ni", "--no_indexes", action="store_true", default=False,
        help="Flag for whether or not to create indexes (add to skip index creation)")
    args = parser.parse_args()

    # Create Pymongo database client and connection
    mc = MongoClient(args.server, args.port)
    db = mc[args.database]
    if args.user and args.password:
        if not db.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(args.user, args.database))
    user_col = db[args.user_collection]
    tweet_col = db[args.tweet_collection]

    # Create Tweepy API
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Populate DB with user data
    populate_user_tweets(api, user_col, tweet_col, args.num_tweets, ensure_indexes=not args.no_indexes)

