"""
Functions to test APIBreakPool (smappPy.tweepy_pool.APIBreakPool)
"""

import tweepy
from tweepy_pool import APIBreakPool, RateLimitException


oauths_file = "/Users/dpb/Dropbox/DuncanPB/twitter/smapp_test_single.json"
api = APIBreakPool(oauths_filename=oauths_file)

def raise_rate_limit():
	"""When called, raises a Tweepy TweepError (rate limit)"""
	raise tweepy.TweepError([{'message': 'Rate Limit Exceeded', 'code': 88}])

def raise_other_error():
	"""When called, raises an anonymous TweepError"""
	raise tweepy.TweepError([{'message': 'Anonymous tweep error', 'code': 12345}])


# SETUP
method_name = "user_timeline"
entities_requested = 600
total_recvd = 0
num_calls = 0

while True:
    print "Querying REST API.user_timeline..."
    shortest_api = api._pick_api_with_shortest_waiting_time_for_method(method_name)
    print "\tShortest API (will be picked for upcoming call): {0}".format(shortest_api)
    print "\tAll APIs: {0}".format(api._apis)

    # Followers (list)
    #cursor = tweepy.Cursor(api.followers, screen_name="taylorswift13")
    # Followers (IDs)
    #cursor = tweepy.Cursor(api.followers_ids, screen_name="taylorswift13")
    # Tweets
    cursor = tweepy.Cursor(api.user_timeline, screen_name="nytimesarts")

    try:
        entities = list(cursor.items(entities_requested))
    except RateLimitException as r:
    	print "\tRate Limit Exception recevied: {0}".format(r)
    	print "\t\terror dict: {0}".format(r.error_dict)
        print "\t\tNumber of calls made before RL: {0}".format(num_calls)
        print "\t\tNumber of entities recvd before RL: {0}".format(total_recvd)
        total_recvd = 0
        num_calls = 0
        continue
    except Exception as e:
        "\tOther error received: {0}".format(e)
        raise(e)
    num_calls += 1
    total_recvd += entities_requested


print "Test complete"
