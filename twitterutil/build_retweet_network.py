"""
Initial code to build retweet networks via networkx

@auth dpb
@date 10/28/2013
"""

import networkx as nx
import matplotlib.pyplot as plt
import smappPy.retweet as rt

from collections import namedtuple

#TODO: Check for username = "" before adding (if so, look at tweet text, fix problem. If "", throw out)
#TODO: Add a threshold (only draws edges if # > THRESHOLD)


def build_retweet_network(tweet_cursor, internal_only=True):
    """
    Takes a pymongo cursor of tweets (a collection that can be iterated over containing tweet dict
    documents). Builds a networkx graph, nodes=users, edges=retweets between users.
    
    By default, creates a network of user-nodes out of only those users that tweeted in the given
    tweet_cursor data set. If internal_only=False, creates a node for all tweeting and retweeted users.

    Note: considers official retweets (via the twitter retweet button) and also, in a best-effort
    sense, manual retweets (via RT tagging).
    """

    num_tweets = tweet_cursor.count(with_limit_and_skip=True)
    if num_tweets < 2:
        print "Warning: fewer than 2 tweets in given set. This will be a small graph"
    elif num_tweets > 10000:
        print "Warning: large number of tweets to consider. This may take a while" 

    # Create user sets (unique user screen_name storage)
    all_users = set()
    result_set_users = set()

    # Create an Edge named-tuple (a simple object/struct)
    Edge = namedtuple("Edge", ["tweeter", "retweeted"])

    # Dict to store retweets (edges). Form: Edge(tweeter, user_retweeted) => Number of retweets 
    retweet_dict = {}
    

    print "Getting user data to build retweet network..."
    for tweet in tweet_cursor:
        if not rt.is_retweet(tweet):
            continue

        tweet_user = tweet['user']['screen_name'].encode('utf-8')
        retweet_user_info = rt.get_user_retweeted(tweet)
        if retweet_user_info == None:
            print "Warning: No retweeted user info for tweet (text: {0})".format(tweet['text'])
            continue
        retweet_user = retweet_user_info[1]

        # Add user data to sets (to keep track of who is in the data set, and who is external)
        all_users.add(tweet_user)
        all_users.add(retweet_user)
        result_set_users.add(tweet_user)

        # Create an Edge for the retweet. Store in retweet dict, counting number of occurrences.
        e = Edge(tweeter=tweet_user, retweeted=retweet_user)
        if e in retweet_dict:
            retweet_dict[e] += 1
        else:
            retweet_dict[e] = 1

    print "Summary:\n"
    print "{0} total users tweeted or retweeted".format(len(all_users))
    print "{0} total users tweeted".format(len(result_set_users))
    print "{0} external users (users that were retweeted but did not tweet in the data set)".format(
            len(all_users.difference(result_set_users)))
    print "{0} directed edges between users".format(len(retweet_dict))
    print "{0} total retweets between all users (including retweeting from same users more than once)\n".format(
            sum(retweet_dict.values()))

    print "Building DiGraph..."
    
    # Create digraph
    DG = nx.DiGraph()

    if internal_only:
        # Add all result_set users only to the graph, with type and color properties
        DG.add_nodes_from(list(result_set_users), node_type="internal", color="#2A2AD1")

        # Add all edges where both tweeter and retweeted are in the user list
        for edge in retweet_dict.items():
            if edge[0].tweeter in result_set_users and edge[0].retweeted in result_set_users:
                DG.add_edge(edge[0].tweeter, edge[0].retweeted, weight=edge[1])

    else:
        # Add all users as nodes, with type property internal (tweeted in result set) or external (just a retweeted user)
        DG.add_nodes_from(list(result_set_users), node_type="internal", color="#2A2AD1")
        DG.add_nodes_from(list(all_users.difference(result_set_users)), node_type="external", color="#CCCCCC")

        # Add all edges, with weight property equal to number of directional retweets between two users (no edge for 0)
        DG.add_weighted_edges_from([ (e[0].tweeter, e[0].retweeted, e[1]) for e in retweet_dict.items() ])

    # Return graph/network!
    return DG

def display_retweet_network(network, outfile=None, show=False):
    """
    Take a DiGraph (retweet network?) and display+/save it to file.
    Nodes must have a 'color' property, represented literally and indicating their type
    Edges must have a 'weight' property, represented as edge width
    """

    # Create a color list corresponding to nodes.
    node_colors = [ n[1]["color"] for n in network.nodes(data=True) ]

    # Get edge weights from graph
    edge_weights = [ e[2]["weight"] for e in network.edges(data=True) ]

    # Build up graph figure
    #pos = nx.random_layout(network)
    pos = nx.spring_layout(network)
    nx.draw_networkx_edges(network, pos, alpha=0.3 , width=edge_weights, edge_color='m')
    nx.draw_networkx_nodes(network, pos, node_size=400, node_color=node_colors, alpha=0.4)
    #nx.draw_networkx_labels(network, pos, fontsize=6)

    plt.title("Retweet Network", { 'fontsize': 12 })
    plt.axis('off')

    if outfile:
        print "Saving network to file: {0}".format(outfile)
        plt.savefig(outfile)

    if show:
        print "Displaying graph. Close graph window to resume python execution"
        plt.show()
