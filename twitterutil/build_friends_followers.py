"""
Script containing functions to populate friend and follower User objects from
a collection of seed users.

@auth dpb
@date 12/01/2014
"""

import logging
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

BSON_NULL = 10

logger = logging.getLogger(__name__)

#TODO: def get_friend_ids_sample(api, user_id, user_doc=None, sample=0.1)
#TODO: Gets sample proportion of friends. Takes userdoc: if None, queries
#TODO: rest API for user, get num friends, iterates over cursor until sample
#TODO: number is hit

#TODO: Add friends_sample param to populate_.... Requires get_friend_ids_sample
#TODO: Add followers_sample param to populate_.... Requires get_followers_ids_sample

#TODO: def get_friends(api, user_id)
#TODO: Gets fully-hydrated friend user docs via Tweepy 'friends' method

#TODO: Add fctly for saving user status of 'no longer valid' or 'not authorized to view'
#TODO: based on twitter response (so can skip these users)


def get_friends_ids(api, user_id):
    """
    Given a Tweepy/smappPy TweepyPool api, query twitter's rest API for friends of
    given user_id. Returns IDs only (much faster / more per request).
    Parameters:
        api     - fully authenticated Tweepy api or smappPy TweepyPool api
        user_id - twitter user id
    Returns tuple: return code, list of IDs or None (if API call fails)
    """
    cursor = Cursor(api.friends_ids, user_id=user_id)
    user_list, ret_code = call_with_error_handling(list, cursor.items())
   
    if ret_code != 0:
        logger.warning("User {0}: Friends request failed".format(user_id))
    
    # Return user list from API or None (call_with_error_handling returns None if
    # call fail)
    return ret_code, user_list


def get_followers_ids(api, user_id):
    """
    Given a Tweepy/smappPy TweepyPool api, query twitter's rest API for followers of
    given user_id. Returns IDs only (much faster / more per request).
    Parameters:
        api     - fully authenticated Tweepy api or smappPy TweepyPool api
        user_id - twitter user id
    Returns tuple: return code, list of IDs or None (if API call fails)
    """
    cursor = Cursor(api.followers_ids, user_id=user_id)
    user_list, ret_code = call_with_error_handling(list, cursor.items())

    if ret_code != 0:
        logger.warning("User {0}: Followers request failed".format(user_id))
    
    # Return user list from API or None (call_with_error_handling returns None if
    # call fail)
    return ret_code, user_list


def populate_friends_from_collection(api, seed_collection, friend_collection, edge_collection=None,
    user_sample=1.0, friends_threshold=20000, update_threshold=None, requery=True,
    print_progress_every=1000):
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
        requery            - If False, only query for user's friends if 'friend_ids' field is empty
        friends_threshold  - If user has > friends_threshold, DO NOT QUERY for friends. If user's
                           - doc does not contain 'friends_count', ignore and query anyway
        update_threshold   - Datetime threshold on users to update. Only queries friends of users
                             with 'friends_updated' field LT 'update_threshold'
    """
    # Ensure indexes
    ensure_userdoc_indexes(seed_collection)
    ensure_userdoc_indexes(friend_collection)
    if edge_collection:
        ensure_edge_indexes(edge_collection)

    # Create cursor over users (sample and date restriction possible)
    users = _get_user_sample(seed_collection, user_sample, "friends_updated", update_threshold)

    # Progress vars
    user_count = users.count(with_limit_and_skip=True)
    user_it = 1
    logger.info("Friends: Considering total {0} users".format(user_count))

    # Iterate over users, get friends, save user and friends
    friend_request_failed_for = []
    for user in users:
        # Print progress
        if user_it % print_progress_every == 0:
            print ".. Processing user {0} of {1}".format(user_it, user_count)
        user_it += 1

        # Check user private/deleted fields - don't requery if unreachable
        if "deleted" in user and user["deleted"] == True:
            logging.info("User {0} deleted, skipping".format(user["id"]))
            continue
        elif "private" in user and user["private"] == True:
            logging.info("User {0} private, skipping".format(user["id"]))
            continue

        # Check requery. If false, and user has friend_ids, skip user
        if not requery and user["friend_ids"]:
            logger.debug("User {0} has friends, not re-querying".format(user["id"]))
            continue

        # Check friends count for threshold
        if "friends_count" in user and user["friends_count"] > friends_threshold:
            logger.info("User {0} has friends {1} above threshold {2}, skipping".format(
                user["id"], user["friends_count"], friends_threshold))
            continue

        r, friend_ids = get_friends_ids(api, user["id"])
        if _check_return_set_user(r, user, seed_collection):
            logging.info("User {0} unreachable, skipping".format(user["id"]))
            continue

        if friend_ids == None:
            friend_request_failed_for.append(user["id"])
            continue

        # Initialize (if necessary) and set user's friend_ids list
        if not user["friend_ids"]:
            user["friend_ids"] = list(set(friend_ids))
        else:
            user["friend_ids"] = list(set(user["friend_ids"] + friend_ids))

        # Save all friends as userdocs in friends collection
        _save_userdocs(friend_ids, friend_collection)

        # Optionally save "edge" documents
        if edge_collection:
            _save_friend_edges(user["id"], friend_ids, edge_collection)

        # Update user doc's timestamps and save
        user["updated_timestamp"] = datetime.now()
        user["friends_updated"] = datetime.now()
        seed_collection.save(user)

    # Print failure numbers
    logger.info("Failed to find friends for {0} users".format(len(friend_request_failed_for)))


def populate_followers_from_collection(api, seed_collection, follower_collection, edge_collection=None,
    user_sample=1.0, followers_threshold=20000, update_threshold=None, requery=True,
    print_progress_every=1000):
    """
    See 'populate_friends_from_collection'. Exactly the same, but for followers
    """
    # Ensure indexes
    ensure_userdoc_indexes(seed_collection)
    ensure_userdoc_indexes(follower_collection)
    if edge_collection:
        ensure_edge_indexes(edge_collection)

    # Create cursor over users (sample and date restriction possible)
    users = _get_user_sample(seed_collection, user_sample, "followers_updated", update_threshold)

    # Progress vars
    user_count = users.count(with_limit_and_skip=True)
    user_it = 1
    logger.info("Considering total {0} users".format(user_count))

    # Iterate over users, get followers, save user and followers
    follower_request_failed_for = []
    for user in users:
        if user_it % print_progress_every == 0:
            print ".. Processing user {0} of {1}".format(user_it, user_count)
        user_it += 1

        # Check user private/deleted fields - don't requery if unreachable
        if "deleted" in user and user["deleted"] == True:
            logging.info("User {0} deleted, skipping".format(user["id"]))
            continue
        elif "private" in user and user["private"] == True:
            logging.info("User {0} private, skipping".format(user["id"]))
            continue

        # Check requery. If false, and user has follower_ids, skip user
        if not requery and user["follower_ids"]:
            logger.debug("User {0} has followers, not re-querying".format(user["id"]))
            continue

        # Check followers count for threshold
        if "followers_count" in user and user["followers_count"] > followers_threshold:
            logger.info("User {0} has followers {1} above threshold {2}, skipping".format(
                user["id"], user["followers_count"], followers_threshold))
            continue


        r, follower_ids = get_followers_ids(api, user["id"])
        if _check_return_set_user(r, user, seed_collection):
            logging.info("User {0} unreachable, skipping".format(user["id"]))
            continue

        if follower_ids == None:
            follower_request_failed_for.append(user["id"])
            continue

        # Initialize (if necessary) and set user's follower_ids list
        if not user["follower_ids"]:
            user["follower_ids"] = list(set(follower_ids))
        else:
            user["follower_ids"] = list(set(user["follower_ids"] + follower_ids))
        
        # Save all followers as userdocs in followers collection
        _save_userdocs(follower_ids, follower_collection)

        # Optionally save "edge" documents
        if edge_collection:
            _save_follower_edges(user["id"], follower_ids, edge_collection)

        # Update user doc's timestamps and save
        user["updated_timestamp"] = datetime.now()
        user["followers_updated"] = datetime.now()
        seed_collection.save(user)

    # Print failure numbers
    logger.info("Failed to find followers for {0} users".format(len(follower_request_failed_for)))


def _get_user_sample(user_collection, user_sample, update_field, update_threshold):
    """
    Takes a collection of userdocs and gets cursor of appropriate sample given
    parameters.
    """
    user_count = user_collection.count()
    if update_threshold:
        users = user_collection.find({"$or": [
                                        {update_field: {"$lt": update_threshold}},
                                        {update_field: {"$type": BSON_NULL}}
                                     ]},
                                     limit=int(user_count * user_sample),
                                     no_cursor_timeout=True)
    else:
        users = user_collection.find(limit=int(user_count * user_sample), no_cursor_timeout=True)

    return users

def _check_return_set_user(ret_val, user_doc, collection):
    """
    Checks return of get_friends/followers call. If specific error messages found,
    (user DNE, user private, etc), sets and saves given userdoc and returns True.
    Otherwise, returns false.
    """
    if ret_val == 34:
        logger.info("User {0} no longer exists, updating userdoc".format(
            user_doc["id"]))
        user_doc["deleted"] = True
        collection.save(user_doc)
        return True
    elif ret_val == 179:
        logger.info("User {0} has private account, updating userdoc".format(
            user_doc["id"]))
        user_doc["private"] = True
        collection.save(user_doc)
        return True
    return False


def _save_userdocs(user_ids, collection):
    """Given a list of user IDs, save userdocs built from IDs to given collection"""
    for uid in user_ids:
        user_doc = create_userdoc(uid)
        try:
            collection.save(user_doc)
        except DuplicateKeyError:
            logger.warn("User {0} already in collection {1}".format(uid, collection.full_name))
        except Exception as e:
            logger.error("Storing User {0} in DB {1} failed".format(uid, collection.full_name))
            logger.error("Exception: {0}".format(e))

def _save_friend_edges(seed_id, friend_ids, collection):
    """Given the seed user and a list of friends, save all 'edges' to collection"""
    for fid in friend_ids:
        edge_doc  = create_edge_doc(seed_id, fid)
        try:
            edge_collection.save(edge_doc)
        except DuplicateKeyError:
            logger.warn("Edge {0} alread in DB {1}, skipping".format(edge_doc, collection.full_name))
        except Exception as e:
            logger.error("Storing Edge {0} in DB {1} failed".format(edge_doc, collection.full_name))
            logger.error("Exception: {0}".format(e))

def _save_follower_edges(seed_id, follower_ids, collection):
    """Given the seed user and a list of followers, save all 'edges' to collection"""
    for fid in follower_ids:
        edge_doc  = create_edge_doc(fid, seed_id)
        try:
            edge_collection.save(edge_doc)
        except DuplicateKeyError:
            logger.warn("Edge {0} alread in DB {1}, skipping".format(edge_doc, collection.full_name))
        except Exception as e:
            logger.error("Storing Edge {0} in DB {1} failed".format(edge_doc, collection.full_name))
            logger.error("Exception: {0}".format(e))


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
    parser.add_argument("-rq", "--requery", action="store_true", default=False,
        help="Whether to query Twitter for frs/fols of users that already have" \
        "frs/fols [False]")
    parser.add_argument("-ppe", "--print_progress_every", type=int,
        default=1000, help="Print progress every Nth user [1000]")
    parser.add_argument("-frt", "--friends_threshold", type=int, default=20000,
        help="Threshold. Do not query for friends of users with more friends than" \
        "this number [20000]")
    parser.add_argument("-fot", "--followers_threshold", type=int, default=20000,
        help="Threshold. Do not query for followers of users with more followers than" \
        "this number [20000]")
    parser.add_argument("-ut", "--update_threshold", type=int, nargs=5, default=None,
        help="If present, only users with friends/followers_updated timestamp BEFORE " \
        "given value will be updated. Format is five numbers, space-separated: " \
        "Year Month Day Hour Minute. EG: 2014 3 15 12 0. (Time in 24-hour format) " \
        "[None]")
    args = parser.parse_args()
    args.update_threshold = datetime(*args.update_threshold) if args.update_threshold else None

    # Set up logging
    logfile = "{0}.{1}".format(args.database, args.seed_collection)
    logfile += ".Friends" if args.friends_collection else ""
    logfile += ".Followers" if args.followers_collection else ""
    logfile += ".log"

    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename=logfile)
    fh.setLevel(logging.DEBUG)
    fm = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                           datefmt="%m/%d/%Y %H:%M:%S")
    fh.setFormatter(fm)
    logger.addHandler(fh)

    logger.info("Friend/Follower collection started on {0}.{1}".format(args.database,
        args.seed_collection))
    logger.info("Passed arguments: {0}".format(args))

    # Set up TweepyPool API
    logger.debug("Loading twitter OAUTHs from {0}".format(args.oauthsfile))
    api = APIPool(oauths_filename=args.oauthsfile, debug=True)

    # Set up DB connection
    logger.debug("Connecting to MongoDB")
    client = MongoClient(args.server, args.port)
    database = client[args.database]
    if args.user and args.password:
        database.authenticate(args.user, args.password)
    seed_collection = database[args.seed_collection]
    edge_collection = database[args.edge_collection] if args.edge_collection else None

    # Attempt friends
    if args.friends_collection:
        logger.info("Populating Friends from {0}".format(seed_collection.full_name))
        friend_collection = database[args.friends_collection]
        populate_friends_from_collection(api, seed_collection, friend_collection, 
            edge_collection=edge_collection, user_sample=1.0, requery=args.requery,
            friends_threshold=args.friends_threshold,
            update_threshold=args.update_threshold,
            print_progress_every=args.print_progress_every)
        logger.info("Friends complete")
    
    # Attempt followers
    if args.followers_collection:
        logger.info("Populating Followers from {0}".format(seed_collection.full_name))
        follower_collection = database[args.followers_collection]
        populate_followers_from_collection(api, seed_collection, follower_collection, 
            edge_collection=edge_collection, user_sample=1.0, requery=args.requery,
            followers_threshold=args.followers_threshold,
            update_threshold=args.update_threshold,
            print_progress_every=args.print_progress_every)
        logger.info("Followers complete")





