"""
Utility functions for pymongo Collections (most functions take pymongo Collection
objects)
"""

from smappPy.tweet_util import ID_FIELD, RANDOM_FIELD, TIMESTAMP_FIELD

def create_tweet_indexes(collection, id=True, random=True, timestamp=True):
    """
    Creates standard indexes on given collection of tweets. Flags for:
        id          unique index on ID_FIELD (default True)
        random      index on RANDOM_FIELD (default True)
        timestamp   index on TIMESTAMP_FIELD (default True)
    """
    collection.ensure_index(ID_FIELD, name="unique_id", unique=True, drop_dups=True, background=True)
    collection.ensure_index(RANDOM_FIELD, name="index_random", background=True)
    collection.ensure_index(TIMESTAMP_FIELD, name="index_timestamp", background=True)