"""
Implements a pooled tweepy API, for using multiple accounts with rate limiting.
"""
import logging
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

    def __init__(self, oauths=None, oauths_filename=None, time_to_wait=15*60, debug=False):
        """
        Instantiate APIPool using either a list of oauths (which are dicts with keys secrets and tokens)
        or using a file which contains these in JSON format.
        """

        self.time_to_wait = time_to_wait

        if oauths_filename:
            with open(oauths_filename) as file:
                oauths = json.load(file)

        oauth_handlers = [self._get_tweepy_oauth_handler(oauth_dict) for oauth_dict in oauths]
        self._apis =[[tweepy.API(oauth_handler), dict()] for oauth_handler in oauth_handlers]

        self.parser = self._apis[0][0].parser

    def _get_tweepy_oauth_handler(self, oauth_dict):
        auth = tweepy.OAuthHandler(oauth_dict["consumer_key"], oauth_dict["consumer_secret"])
        auth.set_access_token(oauth_dict["access_token"], oauth_dict["access_token_secret"])
        return auth

    def _pick_api_with_shortest_waiting_time_for_method(self, method_name):
        ret_api_struct = self._apis[0]
        for api_struct in self._apis:
            if api_struct[1].get(method_name, datetime.min) < ret_api_struct[1].get(method_name, datetime.min):
                ret_api_struct = api_struct
        return ret_api_struct

    def _call_with_throttling_per_method(self, method_name, *args, **kwargs):
        api_struct = self._pick_api_with_shortest_waiting_time_for_method(method_name)
        now = datetime.now()
        throttle_time = api_struct[1].get(method_name, datetime.min)
        time_since_throttle = (now - throttle_time).seconds
        to_wait = self.time_to_wait - time_since_throttle + 1

        if to_wait > 0:
            logging.debug("<{1}>: Rate limits exhausted, waiting {0} seconds".format(to_wait, now.strftime('%H:%M:%S')))
            time.sleep(to_wait)

        try:
            return api_struct[0].__getattribute__(method_name)(*args, **kwargs)
        except TweepError as e:
            if type(e.message) == list and e.message[0]['code'] == RATE_LIMIT_ERROR:
                api_struct[1][method_name] = now
                return self._call_with_throttling_per_method(method_name, *args, **kwargs)
            elif type(e.message) == unicode and json.loads(e.message)['errors'][0]['code'] == RATE_LIMIT_ERROR:
                api_struct[1][method_name] = now
                return self._call_with_throttling_per_method(method_name, *args, **kwargs)
            else:
                raise e

    def __getattribute__(self, name):
        def api_method(*args, **kwargs):
            return self._call_with_throttling_per_method(name, *args, **kwargs)

        if name in tweepy.API.__dict__:
            api_method.pagination_mode = self._pagination_mode_for(name)
            api_method.__self__ = self
            return api_method
        else:
            return object.__getattribute__(self, name)

    def _api_call_supports_pagination(self, name):
        return 'pagination_mode' in self._apis[0][0].__getattribute__(name).__dict__

    def _pagination_mode_for(self,name):
        if self._api_call_supports_pagination(name):
            return self._apis[0][0].__getattribute__(name).pagination_mode
        else:
            return None
