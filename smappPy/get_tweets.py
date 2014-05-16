"""
Functions for getting tweets from Twitter (via REST API), file, and database

@auth dpb
@date 2/24/2014
"""

from bson.json_util import loads
from tweepy import Cursor, TweepError
from json_util import ConcatJSONDecoder


def _check_limit(limit):
    """Checks common 'limit' param to see if is int. Exception if not"""
    if type(limit) != int:
        raise Exception("Limit ({0}) must be an integer".format(limit))


def query_tweets(api, query, limit=None, languages=None):
    """
    Queries twitter REST API for tweets matching given twitter search 'query'.
    Takes an authenticated api object (API or APIPool), a query string, an optional
    limit for number of tweets returned, and an optional list of languages to
    further filter results.
    Returns a cursor (iterator) over Tweepy status objects (not native JSON docs)
    """
    cursor = Cursor(api.search, q=query, include_entities=True, lang=languages)
    if limit:
        _check_limit(limit)
        return cursor.items(limit)
    return cursor.items()


def user_tweets(api, user_id=None, screen_name=None, limit=None):
    """
    Queries Twitter REST API for user's tweets. Returns as many as possible, or
    up to given limit.
    Takes an authenticated API object (API or APIPool), one of user_id or screen_name 
    (not both), and an optional limit for number of tweets returned.
    Returns a cursor (iterator) over Tweepy status objects
    """
    if not (user_id or screen_name):
        raise Exception("Must provide one of user_id or screen_name")
    if user_id:
        cursor = Cursor(api.user_timeline, user_id=user_id)
    elif screen_name:
        cursor = Cursor(api.user_timeline, screen_name=screen_name)
    if limit:
        _check_limit(limit)
        return cursor.items(limit)
    return cursor.items()
    

def geo_tweets():
    """"""
    raise NotImplementedError()


def tweets_from_file(tweetfile):
    """
    Returns a list of tweets read from given file. Tweets are dicts representing json of 
    file contents. For a less-memory intensive version, consider the tweet_from_file_IT() 
    function.
    Note: will not check validity of tweet. Will simply return dict representations of
    JSON entities in the file
    """
    with open(tweetfile) as handle:
        tweets = loads(handle.read(), cls=ConcatJSONDecoder)
    return tweets

def tweets_from_file_IT(tweetfile):
    """
    Returns an iterator for tweets in given tweetfile. Tweets are considered dict
    representations of JSON in given tweetfile
    """
    with open(tweetfile) as handle:
        for line in handle:
            yield loads(line.strip())

def tweets_from_db():
    """"""
    raise NotImplementedError()
