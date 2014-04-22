"""
Utility functions for creating MongoDB indexes on tweet collections
"""

ID_FIELD = "id"
RANDOM_FIELD = "random_number"
TIMESTAMP_FIELD = "timestamp"

def create_all_tweet_indexes(collection, 
                             id_field=ID_FIELD, 
                             random_field=RANDOM_FIELD, 
                             timestamp_field=TIMESTAMP_FIELD,
                             drop_dups=True,
                             background=True):
    """
    Creates all standard tweet collection indexes.
    If drop_dups is true, can remove information (duplicates).
    If background is True, creates indexes in the background.
    Takes a fully authenticated collection object to create index on (must be
    admin-authenticated)
    """
    create_unique_id_index(collection, id_field, drop_dups, background)
    create_random_index(collection, random_field, drop_dups, background)
    create_timestamp_index(collection, timestamp_field, drop_dups, background)


def create_unique_id_index(collection, id_field, drop_dups, background):
    collection.ensure_index(id_field, 
                            name="unique_id", 
                            unique=True, 
                            drop_dups=drop_dups, 
                            background=background)

def create_random_index(collection, random_field, drop_dups, background):
    collection.ensure_index(random_field, 
                            name="index_random", 
                            background=background)

def create_timestamp_index(collection, timestamp_field, drop_dups, background):
    collection.ensure_index(timestamp_field, 
                            name="index_timestamp", 
                            background=background)


