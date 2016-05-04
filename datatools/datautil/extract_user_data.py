"""
Compiles basic user data by day (followers, friends, name, screen name, ID, langauge)

@auth pablo, dpb
@date 04/02/2013
"""



import os
import csv
import argparse
import simplejson as json

from collections import defaultdict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def extract_user_data(collection, outfile, start_date=None, end_date=None, update=10000):
    """
    Extracts user aggregate information from the given collection OF TWEETS, prints basic
    data and outputs a CSV. Fields: ScreenName,Name,UserId,Lang,FriendsCount,FollowersCount,
    Location,NumTweets.
    Takes optional date ranges to constrain query (gte start, lte end. ie, inclusive).
    If only one term specified, take everything before end or after start.
    """
    csv_header = ["ScreenName", "Name", "UserId", "Lang", "FriendsCount", "FollowersCount", "Location", "NumTweets"]

    if start_date and not end_date:
        tweets = collection.find({"timestamp": {"$gte": start_date}})
    elif not start_date and end_date:
        tweets = collection.find({"timestamp": {"$lte": end_date}})
    elif start_date and end_date:
        tweets = collection.find({"timestamp": {"$gte": start_date, "$lte": end_date}})
    else:
        tweets = collection.find()

    user_tweet_count = defaultdict(int)
    user_data = {}
    counter = 1
    num_tweets = tweets.count()
    print "Total collection tweets: {0}".format(collection.count())
    print "Total tweets considered: {0}".format(num_tweets)
    
    print "Compiling user data..."
    for tweet in tweets:
        if counter % update: 
            print ".. Progress: {0:.2%}\r".format(float(counter)/num_tweets),
        counter += 1

        if "user" not in tweet or "id_str" not in tweet["user"]:
            continue
        uid = tweet["user"]["id_str"]
        user_tweet_count[uid] += 1
        user_data[uid] = [tweet['user']['screen_name'].encode("utf8"),
                          tweet['user']['name'].replace(",","").replace("\n","").encode("utf8"),
                          tweet['user']['id_str'],
                          tweet['user']['lang'],
                          tweet['user']['friends_count'],
                          tweet['user']['followers_count'],
                          tweet['user']['location'].replace(",","").replace("\n","").encode("utf8"),
                          user_tweet_count[uid]]

    print "Writing aggregate data to file: '{0}'".format(outfile)
    with open(outfile, "wb") as out_handle:
        csv_handle = csv.writer(out_handle)
        csv_handle.writerow(csv_header)
        for uid, udata in user_data.items():
            csv_handle.writerow(udata)
    print "Complete"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and compile user information")
    parser.add_argument("-s", "--host", action="store", dest="host", default="localhost",
        help="Database server host (default localhost)")
    parser.add_argument("-p", "--port", action="store", type=int, dest="port", default=27017,
        help="Database server port (default 27017)")
    parser.add_argument("-u", "--user", action="store", dest="user", default=None,
        help="Database username (default None, ok when username + pass not required")
    parser.add_argument("-w", "--password", action="store", dest="password", default=None, 
        help="Database password (default None, ok when username + pass not required")
    parser.add_argument("-d", "--db", action="store", dest="database", required=True,
        help="Database containing tweet collection")
    parser.add_argument("-c", "--collection", action="store", dest="collection", required=True,
        help="Collection of tweet data to iterate over")
    parser.add_argument("-o", "--outfile", action="store", dest="outfile", required=True,
        help="File to store CSV user data to")
    parser.add_argument("--update", action="store", type=int, dest="update", default=10000,
        help="Update counter for print output (progress indicator)")
    args = parser.parse_args()

    mc = MongoClient(args.host, args.port)
    db = mc[args.database]
    if args.user and args.password:
        if not db.authenticate(args.user, args.password):
            raise ConnectionFailure(
                "Mongo DB Authentication for User {0}, DB {1} failed".format(args.user, args.database))
    collection = db[args.collection]
    
    extract_user_data(collection, args.outfile, update=args.update)

