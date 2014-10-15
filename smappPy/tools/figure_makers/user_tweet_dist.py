"""
Plot distribution of user tweets in a configured time range
"""

import seaborn as sb
from pymongo import MongoClient
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime

#TODO: MAKE ARGPARSE GO

## CONFIG #####################################################################
start = datetime(2014, 6, 1)
end = datetime(2014, 6, 8)

client = MongoClient("smapp-data.bio.nyu.edu", 27011)
database = client["RandomUsers"]
collection = database["tweets"]
database.authenticate("smapp_readOnly", "smapp_nyu")

plot_super_title = "Random User Collection - User Tweet Distribution"
plot_sub_title = "User tweets 6/01/2014 to 6/10/2014"
transparency = 0.5

print_progress_every = 100000

## MAIN #######################################################################

user_tweet_count = defaultdict(int)

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
