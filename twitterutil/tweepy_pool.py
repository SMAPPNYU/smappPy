"""
Implements a pooled tweepy API, for using multiple accounts with rate limiting.
"""
import json
import time
import oauth
import tweepy
import logging
from datetime import datetime
from tweepy import TweepError
from tweepy_error_handling import parse_tweepy_error


OVER_CAP_ERROR = 130
RATE_LIMIT_ERROR = 88
TOO_MANY_REQUESTS = 429


logger = logging.getLogger(__name__)

class RateLimitException(Exception):
    """Custom rate limit exception for twitter handling"""
    def __init__(self, message, error_dict):
        self.error_dict = error_dict
        super(RateLimitException, self).__init__(message)


class APIPool(object):
    """
    Twitter API Pool.
    This class wraps a pool of `tweepy.api.API` objects, and delegates function calls to them,
    cycling through them when a twitter api rate limit is reached.

    If 'use_appauth' is True, stores additional application-only auth objects in self._apis list
    (such that there is one oauth and one appauth API for each given token).
    (https://dev.twitter.com/oauth/application-only)
    """

    def __init__(self, oauths=None, oauths_filename=None, time_to_wait=15*60,
            use_appauth=True, debug=False):
        """
        Instantiate APIPool using either a list of oauths (which are dicts with keys
        secrets and tokens) or using a file which contains these in JSON format.
        """

        self.time_to_wait = time_to_wait

        if oauths_filename:
            with open(oauths_filename) as file:
                oauths = json.load(file)

        oauth_handlers = [self._get_tweepy_oauth_handler(oauth_dict) for oauth_dict in oauths]
        self._apis =[[tweepy.API(oauth_handler), dict()] for oauth_handler in oauth_handlers]

        if use_appauth:
            appauth_handlers = [self._get_tweepy_appauth_handler(oauth_dict) for oauth_dict in oauths]
            self._apis += [[tweepy.API(appauth_handler), dict()] for appauth_handler in appauth_handlers]

        self.parser = self._apis[0][0].parser

    def __getattribute__(self, name):
        def api_method(*args, **kwargs):
            return self._call_with_throttling_per_method(name, *args, **kwargs)

        if name in tweepy.API.__dict__:
            api_method.pagination_mode = self._pagination_mode_for(name)
            api_method.__self__ = self
            return api_method
        else:
            return object.__getattribute__(self, name)

    def _get_tweepy_oauth_handler(self, oauth_dict):
        try:
            auth = tweepy.OAuthHandler(oauth_dict["consumer_key"], oauth_dict["consumer_secret"])
        except TweepError:
            print TweepError
        auth.set_access_token(oauth_dict["access_token"], oauth_dict["access_token_secret"])
        return auth

    def _get_tweepy_appauth_handler(self, oauth_dict):
        try:
            return tweepy.AppAuthHandler(oauth_dict["consumer_key"], oauth_dict["consumer_secret"])
        except TweepError:
            print TweepError

    def _pick_api_with_shortest_waiting_time_for_method(self, method_name):
        ret_api_struct = self._apis[0]
        for api_struct in self._apis:
            if api_struct[1].get(method_name, datetime.min) < ret_api_struct[1].get(
                    method_name, datetime.min):
                ret_api_struct = api_struct
        return ret_api_struct

    def _call_with_throttling_per_method(self, method_name, *args, **kwargs):
        api_struct = self._pick_api_with_shortest_waiting_time_for_method(method_name)
        now = datetime.now()
        throttle_time = api_struct[1].get(method_name, datetime.min)
        time_since_throttle = (now - throttle_time).seconds
        to_wait = self.time_to_wait - time_since_throttle + 1

        if to_wait > 0:
            logger.debug("<{1}>: Rate limits exhausted, waiting {0} seconds".format(
                to_wait, now.strftime('%H:%M:%S')))
            time.sleep(to_wait)

        try:
            return api_struct[0].__getattribute__(method_name)(*args, **kwargs)
        except TweepError as e:
            error_dict = parse_tweepy_error(e)
            if error_dict["code"] in [RATE_LIMIT_ERROR, TOO_MANY_REQUESTS, OVER_CAP_ERROR]:
                api_struct[1][method_name] = now
                logger.debug("Received limit message: {0}".format(error_dict["message"]))
                return self._call_with_throttling_per_method(method_name, *args, **kwargs)
            else:
                raise(e)

    def _api_call_supports_pagination(self, name):
        return 'pagination_mode' in self._apis[0][0].__getattribute__(name).__dict__

    def _pagination_mode_for(self,name):
        if self._api_call_supports_pagination(name):
            return self._apis[0][0].__getattribute__(name).pagination_mode
        else:
            return None


class APIBreakPool(APIPool):
    """
    A version of APIPool that optionally breaks on rate limits, to allow for more fine-grained
    control of API calls (EG: switching REST Search keyword when rate limit reached on one
    api key).
    """

    def __init__(self, break_on_rate_limit=True, **kwargs):
        """Set break variables, pass all else to superclass"""
        self.break_on_rate_limit = break_on_rate_limit
        super(APIBreakPool, self).__init__(**kwargs)

    def _call_with_throttling_per_method(self, method_name, *args, **kwargs):
        api_struct = self._pick_api_with_shortest_waiting_time_for_method(method_name)
        now = datetime.now()
        throttle_time = api_struct[1].get(method_name, datetime.min)
        time_since_throttle = (now - throttle_time).seconds
        to_wait = self.time_to_wait - time_since_throttle + 1
        if to_wait > 0:
            logger.debug("<{1}>: Rate limits exhausted, waiting {0} seconds".format(
                to_wait, now.strftime('%H:%M:%S')))
            time.sleep(to_wait)
        try:
            return api_struct[0].__getattribute__(method_name)(*args, **kwargs)
        except TweepError as e:
            error_dict = parse_tweepy_error(e)

            if error_dict["code"] in [RATE_LIMIT_ERROR, TOO_MANY_REQUESTS]:
                api_struct[1][method_name] = now
                logger.debug("Received limit message: {0}".format(error_dict["message"]))
                if self.break_on_rate_limit:
                    raise RateLimitException(error_dict["message"], error_dict)
                else:
                    return self._call_with_throttling_per_method(method_name, *args, **kwargs)
            elif error_dict["code"] == OVER_CAP_ERROR:
                api_struct[1][method_name] = now
                logger.debug("Received over cap.: {0}".format(error_dict["message"]))
                return self._call_with_throttling_per_method(method_name, *args, **kwargs)
            else:
                raise(e)