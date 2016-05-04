"""
Functions for getting tweets from Twitter (via REST API), file, and database

@auth dpb and yns
@date 2/17/2015
"""

import logging
from bson.json_util import loads
from tweepy import Cursor, TweepError
from json_util import ConcatJSONDecoder

logger = logging.getLogger(__name__)

def _check_limit(limit):
    """Checks a 'limit' param. If not an int, warns and returns 0 (no limit)"""
    try:
        limit = int(limit)
    except ValueError:
        logger.warn("Given limit {0} not a valid int. Returning full results".format(
            limit))
        return 0
    return limit

def query_tweets(api, query, limit=None, languages=None, **kwargs):
    """
    Queries twitter REST API for tweets matching given twitter search 'query'.
    Takes an authenticated api object (API or APIPool), a query string, an optional
    limit for number of tweets returned, and an optional list of languages to
    further filter results.
    Returns a cursor (iterator) over Tweepy status objects (not native JSON docs)
    """
    cursor = Cursor(api.search, q=query, include_entities=True, lang=languages,
        **kwargs)
    if limit:
        return cursor.items(_check_limit(limit))
    return cursor.items()

def user_tweets(api, user_id=None, screen_name=None, limit=None, **kwargs):
    """
    Queries Twitter REST API for user's tweets. Returns as many as possible, or
    up to given limit.
    Takes an authenticated API object (API or APIPool), one of user_id or screen_name 
    (not both), and an optional limit for number of tweets returned.
    Returns a cursor (iterator) over Tweepy status objects.

    Also takes variable collection of keyword argument to pass on to
    Tweepy/APIPool query methods, to support full API call parameterization.
    """
    if not (user_id or screen_name):
        raise Exception("Must provide one of user_id or screen_name")
    if user_id:
        cursor = Cursor(api.user_timeline, user_id=user_id, count=200,
            **kwargs)
    elif screen_name:
        cursor = Cursor(api.user_timeline, screen_name=screen_name,
            count=200, **kwargs)
    if limit:
        return cursor.items(_check_limit(limit))
    return cursor.items()

def place_tweets(api, place_list=None, query="", granularity=None, limit=None):
    """
    Queries Twitter REST API for tweets based on a name of a place or a list of place names.
    Takes an authenticated API object(API or APIPool not both), and an optional 
    limit for the number of tweets returned.
    Takes a place_list of names of places in the world. 
    It is crucial to note that for a place_list the limit applies to each
    location, and not over all locations. 
    For example a query to ["Kyiv", "San Francisco"] would have a limit of 5
    for the first query to Kyiv and 5 for the second query to San Francisco.
    Returns an array whose elements are iterators over the elements of each 
    place in the original place_list.
    ["Kyiv", "San Francisco"] returns[Kyiv_Iterator_Obj, SanFrancisco_Iterator_Obj]
    """

    if not (place_list):
        raise Exception("Hey hotshot slow down! You're missing a place_list input.")

    locations_iterators = (query_tweets(api, query=query+"&place:%s" % api.geo_search(query=place, max_results=limit, granularity=granularity)[0].id, limit=limit) 
                        for place in place_list)
    return (tweet for it in locations_iterators for tweet in it)

def georadius_tweets(api, georadius_list=None, query="", limit=None):
    """
    Queries Twitter REST API for tweets within a radius of two coordinates.
    Takes an authenticated API object (API or APIPool), and a geo-object which
    two coordinates and a radius or a list of geo-objects , and a limit on 
    the number of queries for each georadius.
    Returns a list whose elements are iterators over the results from each
    provided georadius.
    """

    if not(georadius_list):
        raise Exception("Hey city slicker! You're missing a georadius_list input.")
    
    locations_iterators = (query_tweets(api, query=query+"&geocode:%s" % ",".join(str(elem) for elem in georadius), limit=limit) 
                        for georadius in georadius_list)
    return (tweet for it in locations_iterators for tweet in it)

def tweets_from_BSON_file_IT(tweetfile):
    """
    Returns an iterator over tweets from the given raw Mongo BSON file.
    """
    raise NotImplementedError()

def tweets_from_JSON_file(tweetfile):
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

def tweets_from_JSON_file_IT(tweetfile):
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
