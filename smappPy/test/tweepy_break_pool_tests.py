"""
Functions to test APIBreakPool (smappPy.tweepy_pool.APIBreakPool)
"""

import tweepy
from tweepy_pool import APIBreakPool, RateLimitException


oauths_file = "/Users/dpb/Dropbox/DuncanPB/twitter/smapp_recovery_auths.json"
api = APIBreakPool(oauths_filename=oauths_file)
method_name = "followers"

def raise_rate_limit():
	"""When called, raises a Tweepy TweepError (rate limit)"""
	raise tweepy.TweepError([{'message': 'Rate Limit Exceeded', 'code': 88}])

def raise_other_error():
	"""When called, raises an anonymous TweepError"""
	raise tweepy.TweepError([{'message': 'Anonymous tweep error', 'code': 12345}])

while True:
    print "Querying REST API.user_timeline..."
    shortest_api = api._pick_api_with_shortest_waiting_time_for_method(method_name)
    print "\tShortest API (will be picked for upcoming call): {0}".format(shortest_api)

    cursor = tweepy.Cursor(api.followers, screen_name="nytimesarts")
    try:
        tweets = list(cursor.items(1000))
    except RateLimitException as r:
    	print "\tRate Limit Exception recevied: {0}".format(r)
    	print "\t\terror dict: {0}".format(r.error_dict)
    except Exception as e:
        "\tOther error received: {0}".format(e)
        raise(e)

print "Test complete"
