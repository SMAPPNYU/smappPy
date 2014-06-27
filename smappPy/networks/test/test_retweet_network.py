"""
Simple script to test user-retweet network build (no unittest as of yet)

@auth dpb
@date 10/28/2013
"""

# Set up MongoConnection, get a set of results
from pymongo import MongoClient
client = MongoClient("smapp.politics.fas.nyu.edu", 27011)
database = client["US_LEGISLATOR"]
database.authenticate("readonly", "smappnyu")

from datetime import datetime
start = datetime(2013,9,20)
end = datetime(2013,9, 22)
results = database.legislator_tweets.find({"timestamp": {"$gte": start, "$lt": end}})

# Pass results to nework building function, get graph
from tweetnetworks.build_retweet_network import build_retweet_network, display_retweet_network
retweet_net = build_retweet_network(results, internal_only=False)

# Print and show graph, with coloring
display_retweet_network(retweet_net, outfile="/home/dpb/Desktop/legislator-shutdown-retw.pdf", show=True)

# Export network in GEXF format (for gephi)
import networkx as nx
nx.write_gexf(retweet_net, "/home/dpb/Desktop/legislator-shutdown-retw.gexf", prettyprint=True)
