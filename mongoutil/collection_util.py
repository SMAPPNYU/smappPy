"""
Utility functions for pymongo Collections (most functions take pymongo Collection
objects)
"""

from smappPy.tweet_util import ID_FIELD, RANDOM_FIELD, TIMESTAMP_FIELD
from smappPy.twitteruser_util import USER_ID, USER_RANDOM, ACCOUNT_CREATED_TIMESTAMP

def create_tweet_indexes(collection, index_id=True, index_random=True, index_timestamp=True):
    """
    Creates standard indexes on given collection of tweets. Flags for:
        id          unique index on ID_FIELD (default True)
        random      index on RANDOM_FIELD (default True)
        timestamp   index on TIMESTAMP_FIELD (default True)
    """
    if index_id:
        collection.ensure_index(ID_FIELD,
                                name="unique_id",
                                unique=True,
                                drop_dups=True,
                                background=True)
    if index_random:
        collection.ensure_index(RANDOM_FIELD,
                                name="index_random",
                                background=True)
    if index_timestamp:
        collection.ensure_index(TIMESTAMP_FIELD,
                                name="index_timestamp",
                                background=True)

def create_user_indexes(collection, index_id=True, index_random=True, index_timestamp=True):
    """
    Creates standard indexes on collections of twitter user data. Flags for:
        id          unique index on user USER_ID field
        random      index on USER_RANDOM field
        timestamp   index on ACCOUNT_CREATED_TIMESTAMP field
    """
    if index_id:
        collection.ensure_index(USER_ID,
                                name="unique_id",
                                unique=True,
                                drop_dups=True,
                                background=True)
    if index_random:
        collection.ensure_index(USER_RANDOM,
                                name="index_random",
                                background=True)
    if index_timestamp:
        collection.ensure_index(ACCOUNT_CREATED_TIMESTAMP,
                                name="index_timestamp",
                                background=True)