"""
To start from scratch (dropping existing db):
    python build_follower_network.py -db test -uc stoltenberg_network -a ~/jo-twitter.json -if stoltenberg.txt --from-scratch

To output GraphML:
    python build_follower_network.py -db test -uc stoltenberg_network --output > stoltenberg.graphml
"""

import re
import sys
import math
import random
import logging
import argparse
import networkx as nx
from tweepy import Cursor
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from smappPy.iter_util import grouper
from smappPy.tweepy_pool import APIPool
from smappPy.date import mongodate_to_datetime
from smappPy.tweepy_error_handling import call_with_error_handling

def generate_output_file(users_collection, edges_collection, keep_empty_nodes):
    graph = nx.DiGraph()
    nonempty_user_ids = set()

    for user in users_collection.find():
        nonempty_user_ids.add(user['id'])

        attrs_to_keep = [
            'name',
            'id',
            'geo_enabled',
            'followers_count',
            'protected',
            'lang',
            'utc_offset',
            'statuses_count',
            'friends_count',
            'screen_name',
            'url',
            'location',
            ]
        user_attrs = { key : user[key] or '' for key in attrs_to_keep }
        graph.add_node(user['id'], attr_dict=user_attrs)

    for edge in edges_collection.find():
        if keep_empty_nodes or edge['from'] in nonempty_user_ids and edge['to'] in nonempty_user_ids:
            graph.add_edge(edge['from'], edge['to'])

    nx.write_graphml(graph, sys.stdout)

def crawl(users_collection, edges_collection, user_ids, twitter_api, depth=1, percentage=1, sample_more=False, get_friends=False, get_followers=True):
    """
    For each user in `user_ids`, gets all followers_ids and friends_ids and stores the edges in db.
    If 'get_followers' is True, it then also store a `percentage` sample of each user's followers in the db.
    If 'get_friends' is True, it then also store a `percentage` sample of each user's friends in the db.

    Do this for `depth` recursive iterations for each user that is stored in the database. The last level
    of users stored in the database will have edges for their friends/followers, but those won't be sampled
    and fetched to db.
    """
    users, code = call_with_error_handling(ensure_users_in_db, user_ids, users_collection, twitter_api)
    if code != 0:
        logging.warn("Some error looking up some users, code {}".format(code))
        #TODO how should this be dealt with? does twitter return the OK ones or nothing?
        #IDEA users = ensure_users_one_by_one(user_ids, users_collection, twitter_api)
    for user in users:
        if 'sampled_followers' in user and user['sampled_followers'] and not sample_more:
            logging.info(".. already sampled this user's followers. moving on.")
            continue

        ids_tup, code = call_with_error_handling(ensure_users_edges_in_db, user, edges_collection, twitter_api)
        if code != 0:
            logging.warn(".. Some problem getting user {0}'s followers. Maybe she's protected or something. Skipping.".format(user['id']))
            continue
        friends_ids, followers_ids = ids_tup
        user['sampled_followers'] = True
        users_collection.save(user)

        other_user_ids = []
        if get_friends:
            other_user_ids += random.sample(friends_ids, int(math.ceil(percentage * len(friends_ids))))
        if get_followers:
            other_user_ids += random.sample(followers_ids, int(math.ceil(percentage * len(followers_ids))))

        if depth > 0 and other_user_ids:
            crawl(users_collection, edges_collection, other_user_ids, twitter_api, depth-1, percentage, sample_more, get_friends, get_followers)


def ensure_users_edges_in_db(user, edges_collection, twitter_api):
    "Looks up a user's friends_ids and followers_ids on the twitter api, and stores the edges in db."

    logging.info(".. Fetching followers_ids for user {0}.".format(user['id']))
    logging.info(".... user has {0} followers.".format(user['followers_count']))
    cursor = Cursor(twitter_api.followers_ids, id=user['id'])
    edges = [{ 'from' : follower_id,
               'to'   : user['id']}
            for follower_id in cursor.items()]
    store_edges(edges_collection, edges)
    followers_ids = [edge['from'] for edge in edges]

    logging.info(".. Fetching friends_ids for user {0}.".format(user['id']))
    logging.info(".... user has {0} friends.".format(user['friends_count']))
    cursor = Cursor(twitter_api.friends_ids, id=user['id'])
    edges = [{ 'to'   : friend_id,
               'from' : user['id']}
            for friend_id in cursor.items()]
    store_edges(edges_collection, edges)
    friends_ids = [edge['to'] for edge in edges]

    return friends_ids, followers_ids

def store_edges(collection, edges):
    try:
        if edges:
            collection.insert(edges, continue_on_error=True)
    except DuplicateKeyError as e:
        #  e.message is "E11000 duplicate key error index: test.test_collection.$compound_unique  dup key: { : 1, : 2 }""
        edge = re.match(r'.*: (\d+), : (\d+).*', e.message).groups()
        logging.warn(".... duplicate edge ({edge[0]} -> {edge[1]}) cannot be saved to db, skipped it".format(edge=edge))
    logging.info(".... edges persisted to db")

def ensure_users_in_db(user_ids, collection, api):
    "Return user objects from mongodb collections. Users that aren't yet in mongo are looked up."
    logging.info("Fetching {} users..".format(len(user_ids)))
    existing_users = list(collection.find( { 'id' : { '$in' : user_ids } } ))
    new_users_ids = set(user_ids) - { user['id'] for user in existing_users }
    if new_users_ids:
        logging.info(".. {} users not in database. Looking up on twitter api.".format(len(new_users_ids)))
        new_users = []
        for user_ids_slice in grouper(100, new_users_ids, pad=False):
            users = [augment_user(user) for user in api.lookup_users(user_ids = user_ids_slice)]
            store_users(collection, users)
            new_users += users

        return existing_users + new_users
    else:
        logging.info(".. All users already in database.")
        return existing_users

def store_users(collection, users):
    try:
        if users:
            ids = collection.insert(users, continue_on_error=True)
    except DuplicateKeyError as e:
        logging.warn(".... some user(s) not saved: {}".format(e.message))
    logging.info(".... {} users persisted to db".format(len(ids)))

def ensure_user_in_db(user_id, collection, api):
    "Returns user object from mongodb if it exists. If not, looks up on twitter api, stores the new user object, and returns it."
    logging.info("Looking at user {0}.".format(user_id))

    user = collection.find_one( { 'id' : user_id } )
    if not user:
        logging.info(".. wasn't yet in database, looking up.")
        user = lookup_user(api, user_id)
        store_user(user, collection)
    return user

def store_user(user, collection):
    try:
        collection.insert(user)
    except Exception, e:
        logging.warn("Error storing user {id}".format(id=user['id']))

def lookup_user(api, user_id):
    "Lookup the user in the twitter api and return that object augmented with random field and timestamps."
    user = api.get_user(id=user_id)
    augmented_user = augment_user(user)
    return augmented_user

def augment_user(user):
    raw_user = user._json
    raw_user["updated_timestamp"] = datetime.now()
    raw_user["created_at_timestamp"] = mongodate_to_datetime(raw_user["created_at"])
    raw_user["random_number"] = random.random()
    return raw_user

def get_mongo_collection(args):
    mc = MongoClient(args.host, args.port)
    db = mc[args.database]
    if args.user and args.password:
        if not db.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(args.user, args.database))
    nodes_collection = db[args.collection_prefix + '_nodes']
    edges_collection = db[args.collection_prefix + '_edges']

    if args.from_scratch:
        nodes_collection.drop()
        edges_collection.drop()

    ensure_indexing(nodes_collection, edges_collection)

    return nodes_collection, edges_collection

def ensure_indexing(nodes_collection, edges_collection):
    nodes_collection.ensure_index("id", name="unique_id", unique=True, drop_dups=True, background=True)
    nodes_collection.ensure_index("random", name="random_number", background=True)
    edges_collection.ensure_index([('from', ASCENDING),("to", ASCENDING)], name="compound_unique",
                                    unique=True, drop_dups=True, background=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl twitter to build follower network")
    parser.add_argument("-s", "--server", action="store", dest="host", default="localhost",
        help="Database server to store in (default localhost)")
    parser.add_argument("-p", "--port", action="store", type=int, dest="port", default=27017,
        help="Database server port (default 27017)")
    parser.add_argument("-u", "--user", action="store", dest="user", default=None,
        help="Database username (default None, ok when username + pass not required")
    parser.add_argument("-w", "--password", action="store", dest="password", default=None, 
        help="Database password (default None, ok when username + pass not required")
    parser.add_argument("-db", "--database", action="store", dest="database", required=True,
        help="Database name")
    parser.add_argument("-uc", "--user-collection", action="store", dest="collection_prefix", required=True,
        help="Collection prefix (will use prefix_nodes and prefix_edges")
    parser.add_argument("-if", "--seed-file", action="store", dest="seed_file", required=False,
        help="Path to file containing line-delimited twitter-ids of users to start building network from.")
    parser.add_argument("-pc", "--percentage", action="store", dest="percentage", default=1,
        help="Percentage of followers to fetch when building graph. The program will fetch *at least* \
        this percentage of followers and friends.")
    parser.add_argument("-sm", "--sample-more", action="store", dest="sample_more", default=False,
        help="Whether or not to get another percentage of users followers, if this is not the first run of the program. Default False.")
    parser.add_argument("-a", "--oauthsfile", action="store", dest="oauthsfile", required=False,
        help="JSON file w/ list of OAuth keys (consumer, consumer secret, access token, access secret)")
    parser.add_argument("-d", "--depth", action="store", type=int, dest="depth", default=1,
        help="depth of network to collect from initial seed")
    parser.add_argument("--from-scratch", dest='from_scratch', action='store_const',
                   const=True, default=False,
                   help='Drop the database before starting. Will drop database! Use with caution! Default False.')
    parser.add_argument("--output", dest='action', action='store_const',
                   const='output', default='collect',
                   help='Output a graph file from the specified Mongo collection (default: crawl twitter and save to that db)')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s--%(levelname)s: %(message)s', level=logging.DEBUG)

    nodes_collection, edges_collection = get_mongo_collection(args)

    if args.action == 'output':
        generate_output_file(nodes_collection, edges_collection, False)
    else:
        if not args.seed_file or not args.oauthsfile:
            parser.error('Specify OAUTHSFILE and SEED_FILE for network collection')

        seed = [int(line) for line in open(args.seed_file).readlines()]

        twitter_api = APIPool(oauths_filename=args.oauthsfile, debug=True)
        crawl(nodes_collection, edges_collection, seed, twitter_api, args.depth, float(args.percentage)/100, args.sample_more)
