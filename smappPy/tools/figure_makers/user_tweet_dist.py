"""
Plot distribution of user tweets in a configured time range
"""

import argparse
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from pymongo import MongoClient
from collections import defaultdict

## COMMANDLINE ################################################################
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user", default="smapp_readOnly")
parser.add_argument("-w", "--password", required=True)
args = parser.parse_args()

## CONFIG #####################################################################
start = datetime(2014, 6, 1)
end = datetime(2014, 6, 8)

client = MongoClient("smapp-data.bio.nyu.edu", 27011)
database = client["RandomUsers"]
collection = database["tweets"]

plot_super_title = "Random User Collection - User Tweet Distribution"
plot_sub_title = "User tweets 6/01/2014 to 6/10/2014"
transparency = 0.5

print_progress_every = 100000

## MAIN #######################################################################

# Auth to DB
if not database.authenticate(args.user, args.password):
    raise Exception("DB authentication failed")

# Init user tweet count dict
user_tweet_count = defaultdict(int)

# Query DB for tweets, iterate to count
tweets = collection.find({"timestamp": {"$gte": start, "$lt": end}})
total_count = tweets.count(with_limit_and_skip=True)
print "Considering {0} tweets in range {1} - {2}".format(
    total_count, start, end)

i = 0
for tweet in tweets:
    if i % print_progress_every == 0:
        print "Considering {0} of {1}".format(i, total_count)
    i += 1

    if "user" not in tweet or "id" not in tweet["user"]:
        continue
    
    user_tweet_count[tweet["user"]["id"]] += 1

# Plot and show
n, bins, patches = plt.hist(user_tweet_count.values(), 
                            bins=30, 
                            log=True, 
                            normed=False, 
                            facecolor="green", 
                            alpha=transparency, 
                            align="right")

plt.tick_params(axis="both", which="both", bottom="off", top="off", left="off", right="off")
plt.xlabel("Tweet/Day frequency")
plt.ylabel("Log(Number users)")
plt.suptitle(plot_super_title)
plt.title(plot_sub_title)
plt.show()
