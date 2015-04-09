"""
Module for building up collection of fully-populated twitter User objects
and storing to DB.

@auth dpb
@date 12/01/2014
"""

import time
import random
import argparse

from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
from smappPy.iter_util import grouper
from smappPy.user_collection import ensure_userdoc_indexes
from smappPy.tweepy_error_handling import call_with_error_handling

CAPACITY_WAIT = 30

def populate_user_collection_from_collection(api, seed_collection, store_collection, num_passes=2,
    not_found_file=None, sample=1.0):
    """
    Populates a user collection (queries Twitter for all fully-hydrated user objects, then saves)
    from the docs in given seed_collection. Docs in seed collection must have an 'id' field
    representing a Twitter User ID. 
    Note: seed_collection and store_collection can be the same collection (in which case, userdocs
    in the seed collection are updated with data from Twitter)
    """
    # Define user IDs iterable
    class UserIDIterator:
        def __iter__(self, ):
            for u in seed_collection.find(fields={"_id": False, "id": True}):
                yield u["id"]

    # Call populate...
    populate_user_collection_from_ids(api, store_collection, UserIDIterator(), num_passes, not_found_file)


def populate_user_collection_from_ids(api, collection, user_ids, num_passes=2, not_found_file=None,
    sample=1.0):
    """
    Populates a collection (Pymongo collection object, fully connected and authenticated)
    with user data from the twitter REST API endpoint /users/show (removes 'status' - user's
    most recent tweet).
    Parameters:
        api         - Tweepy or smappPy TweepyPool API object, fully authenticated 
        collection  - Pymongo collection object, fully connected and authenticated
        users       - Iterable of twitter user IDs to populate. Will pull totally into memory
        num_passes  - Number of retries on UIDs failing to come in the first time
        not_found_file - Filename to store all user IDs not found, line separated. If None, no output
        sample      - Proportion of users in user_ids list to populate, sampled randomly. Rounded DOWN
    """

    # Ensure standard userdoc indexes on collection
    ensure_userdoc_indexes(collection)

    # Set up list of users not yet retrieved from Twitter and passes counter
    users_not_found = list(set([str(i) for i in user_ids]))
    if sample < 1.0:
        users_not_found = random.sample(users_not_found, int(len(users_not_found) * sample))
    passnum = 0
    
    # User-fetching loop
    while len(users_not_found) > 0 and num_passes > passnum:

        print "Pass {0}, attempting to find {1} users".format(passnum, len(users_not_found))
        users_found_this_pass = []
        
        for user_group in grouper(100, users_not_found, pad=False):
            user_list, return_code = call_with_error_handling(api.lookup_users, user_ids=user_group)
            if return_code == 130:
                print ".. Twitter over capacity. Sleeping {0} seconds".format(CAPACITY_WAIT)
                time.sleep(CAPACITY_WAIT)
                continue
            elif return_code != 0:
                print ".. Error {0}. Continuing".format(return_code)
                continue

            for user in user_list:
                if not user or not user._json:
                    continue
                users_found_this_pass.append(str(user.id))

                userdoc = create_userdoc_from_twitter_user(user._json)
                try:
                    collection.save(userdoc)
                except DuplicateKeyError as e:
                    print ".. User {0}: already exists in DB. Skipping".format(user.id)
                    continue

        # Remove found users from users not found list
        users_not_found = list(set(users_not_found) - set(users_found_this_pass))
        passnum += 1

    # Report and finish
    print "Total users not found: {0}".format(len(users_not_found))
    if not_found_file and len(users_not_found) > 0:
        print "Writing IDs not found to file: {0}".format(not_found_file)
        with open(not_found_file, "w") as handle:
            for uid in users_not_found:
                handle.write("{0}\n".format(uid))
    print "Complete"
