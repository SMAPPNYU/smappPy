"""
Implements a pooled tweepy API, for using multiple accounts with rate limiting.
"""

import tweepy
import oauth
import json
import time
from datetime import datetime
from tweepy import TweepError

RATE_LIMIT_ERROR = 88

class APIPool(object):
	"""
	Twitter API Pool.
	This class wraps a pool of `tweepy.api.API` objects, and delegates function calls to them,
	cycling through them when a twitter api rate limit is reached.
	"""

	def __init__(self, oauths=None, oauths_filename=None, time_to_wait=15*60):
		"""
		Instantiate APIPool using either a list of oauths (which are dicts with keys secrets and tokens)
		or using a file which contains these in JSON format.
		"""

		self.time_to_wait = time_to_wait

		if oauths_filename:
			with open(oauths_filename) as file:
				oauths = json.load(file)

		oauth_handlers = [self._get_tweepy_oauth_handler(oauth_dict) for oauth_dict in oauths]
		self.apis = [[tweepy.API(oauth_handler), datetime.min] for oauth_handler in oauth_handlers]

	def _get_tweepy_oauth_handler(self, oauth_dict):
		auth = tweepy.OAuthHandler(oauth_dict["consumer_key"], oauth_dict["consumer_secret"])
		auth.set_access_token(oauth_dict["access_token"], oauth_dict["access_token_secret"])
		return auth

	def _pick_api_with_shortest_waiting_time(self):
		ret_idx, (ret_api, ret_throttled_at) = 0, self.apis[0]
		for idx, (api, throttled_at) in enumerate(self.apis):
			if throttled_at < ret_throttled_at:
				ret_api, ret_throttled_at, ret_idx = api, throttled_at, idx
		return ret_api, ret_throttled_at, ret_idx

	def _call_with_throttling(self, method_name, *args, **kwargs):
		now = datetime.now()
		api, throttled_at, idx = self._pick_api_with_shortest_waiting_time()
		time_since_throttle = (now - throttled_at).seconds
		to_wait = self.time_to_wait - time_since_throttle + 1

		if to_wait > 0:
			time.sleep(to_wait)
		try:
			return api.__getattribute__(method_name)(*args, **kwargs)
		except TweepError as e:
			if e.message[0]['code'] == RATE_LIMIT_ERROR:
				self.apis[idx][1] = now
				return self._call_with_throttling(method_name, *args, **kwargs)
			else:
				raise e

	def __getattribute__(self, name):
		def api_method(*args, **kwargs):
			return self._call_with_throttling(name, *args, **kwargs)

		if name in tweepy.API.__dict__:
			return api_method
		else:
			return object.__getattribute__(self, name)
