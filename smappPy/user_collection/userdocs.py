"""
Contains user docs for user collections, and supporting functions

@auth dpb
@date 12/01/2014
"""

import random
from datetime import datetime
from smappPy.date import mongodate_to_datetime

# Global of userdoc fields and functions that generate default values
userdoc_fields_defaults = {
    "id": lambda: None,
    "deleted": lambda: False,
    "private": lambda: False,
    "random_number": lambda: random.random(),
    "created_at_timestamp": lambda: None,
    "updated_timestamp": lambda: datetime.now(),
    "tweet_ids": lambda: None,
    "latest_tweet_id": lambda: None,
    "tweet_frequency": lambda: 0.0,
    "tweets_updated": lambda: None,
    "friend_ids": lambda: None,
    "follower_ids": lambda: None,
    "friends_updated": lambda: None,
    "followers_updated": lambda: None,
}

def ensure_userdoc_indexes(collection, unique_id=True, random=True, updatedTS=True):
    """Creates or checks common indexes for user collection docs"""
    if unique_id:
        collection.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)
    if random:
        collection.ensure_index("random_number", name="index_random", background=True)
    if updatedTS:
        collection.ensure_index("updated_timestamp", name="index_updated", background=True)

def create_userdoc(user_id):
    """Returns basic user doc populated with given ID (can pass null IDs)"""
    userdoc = {}
    for field, default_func in userdoc_fields_defaults.items():
        userdoc[field] = default_func()
    userdoc["id"] = int(user_id) if user_id else userdoc_fields_defaults["id"]()
    return userdoc

def create_userdoc_from_twitter_user(twitter_user, delete_status=True):
    """
    Takes a fully hydrated Twitter user document, adds user collection userdoc fields,
    and transforms twitter user fields (created_at to timestamp, etc).
    twitter_user    - JSON (dict) representing twitter user object
    Returns modified object (not strictly necessary, modifies in-place)
    """
    # Add fields
    for field, default_func in userdoc_fields_defaults.items():
        if field in twitter_user:
            continue
        twitter_user[field] = default_func()
    
    # Set 'created_at_timestamp'
    twitter_user["created_at_timestamp"] = mongodate_to_datetime(twitter_user["created_at"])

    # Delete status object (conditionally)
    if delete_status:
        del(twitter_user["status"])

    return twitter_user

def format_userdoc_collection(collection, delete_status=True):
    """
    Iterate over userdocs in given collection. Ensure they have correct userdoc fields
    and are well-formated (no 'status', etc)
    """
    print "Processing {0} userdocs from {1}".format(collection.count(), collection)
    for userdoc in collection.find():
        if delete_status:
            if "status" in userdoc:
                del(userdoc["status"])

        for field, default_func in userdoc_fields_defaults.items():
            if field not in userdoc:
                userdoc[field] = default_func()

        collection.save(userdoc)
    print "Complete"
