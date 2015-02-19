"""
Functions for getting tweets from Twitter (via REST API), file, and database

@auth dpb and yns
@date 2/17/2015
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

def geo_tweets(api, geoloc_list=None, single_geoloc=None, query=None, granularity=None, limit=None):
    """
    Queries Twitter REST API for tweets based on a name of a place or a list of place names.
    Takes an authenticated API object(API or APIPool not both), and an optional 
    limit for the number of tweets returned.
    Takes either a list of Geo locations (placenames) or a single geolocation.
    Also takes the granularity (city, admin or country), this can be omitted but 
    should be included for more accurate twitter queries. In the future it would 
    be nice to be able to take different granularities for different places in a 
    geoloc_list.
    It is crucial to note that for a geoloc_list the limit applies to each
    geolocation, and not over all geolocations. 
    For example a query to ["Kyiv", "San Francisco"] would have a limit of 5
    for the first query to Kyiv and 5 for the second query to San Francisco.
    Returns an array whose elements are equivalent to the combined
    cursor.items() calls of all the places in the list.
    """

    locations = []
    if not (geoloc_list or single_geoloc or query):
        raise Exception("Hey hotshot slow down! You're missing a geoloc_list, single_geoloc, or query input.")
    if geoloc_list:
        for place in geoloc_list:
            placeid_search = api.geo_search(query=place, max_results=limit, granularity=granularity)
            place_id = placeid_search[0].id # 0 gets the most likely place, not error proof
            tweets_from_place = query_tweets(api, query=query+"&place:%s" % place_id, limit=limit)
            locations.extend(tweets_from_place)
    elif single_geoloc:
        placeid_search = api.geo_search(query=single_geoloc, max_results=limit, granularity=granularity)
        place_id = placeid_search[0].id # 0 gets the most likely place, not error proof
        tweets_from_place = query_tweets(api, query=query+"&place:%s" % place_id, limit=limit)
        locations.extend(tweets_from_place)
    return locations

def georadius_tweets(api, georadius_list=None, single_georadius=None, query=None, limit=None):
    """
    Queries Twitter REST API for tweets within a box of bounding cooridnates.
    Takes an authenticated API object (API or APIPool), and a geo-object which
    two coordinates and a radius or a list of geo-objects , and a limit on 
    the number of queries for each box.
    Returns an array whose elements are equivalent to the combined
    cursor.items() calls of all the boxes in the list.
    """
    locations = []
    if not(single_georadius or georadius_list):
        raise Exception("Hey city slicker! You're missing a single_georadius or geobox_list input.")
    elif georadius_list:
        for georadius in georadius_list:

            for i in range(0, len(georadius)):
                georadius[i] = str(georadius[i])

            tweets_from_place = query_tweets(api, query=query+"&geocode:%s" % ",".join(georadius), limit=limit)
            locations.extend(tweets_from_place)

    elif single_georadius:

        for i in range(0, len(single_georadius)):
            single_georadius[i] = str(single_georadius[i])

        tweets_from_place = query_tweets(api, query=query+"&geocode:%s" % ",".join(single_georadius), limit=limit)
        locations.extend(tweets_from_place)
    return locations

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
