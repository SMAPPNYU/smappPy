"""
Tweet filter module,
contains common shared tweet filter functions

Functions and docstrings parsed directly by the web dashboard for adding these to tweet collector.

2014/11/19 @jonathanronen
"""

def field_contains(tweet, field, *terms):
    """
    Returns true if the text in tweet[field] contains any of the terms given.

    `field` may be any attribute of tweets, for instance:
        field_contains(tweet, 'text', 'nyc')
        # will return True for tweets containing nyc

    `field` may also be a path to a nested attribute, for instance:
        field_contains(tweet, 'user.screen_name', 'bob', 'alice')
        # will return True for usernames with bob or alice in them.
    """
    path = field.split('.')
    value = tweet[path.pop(0)]
    for p in path[1:]:
        value = value[p]
    return any(term in value for term in terms)

def user_location_contains(tweet, *terms):
    """
    True if tweet['user']['location'] contains any of the terms.
    """
    return field_contains('user.location', *terms)

def user_description_contains(tweet, *terms):
    """
    True if tweet['user']['description'] contains any of the terms.
    """
    return field_contains('user.description', *terms)

def within_geobox(tweet, sw_lon, sw_lat, ne_lon, ne_lat):
    """
    True if tweet is geotagged and is sent within the box specified by GeoJSON points (longitude, latitude)
    (sw_lon, sw_lat)  <-  the southwest corner
    (ne_lon, ne_lat)  <-  the northeast corner

    Example:
    ========
    from smappPy.geo_tweet import GeoBox_Philadelphia
    within_geobox(tweet, *GeoBox_Philadelphia)
    # true for tweets tweeted within a box surrounding philly
    """
    if 'coordinates' not in tweet or 'coordinates' not in tweet['coordinates']:
        return False
    coords = tweet['coordinates']['coordinates']
    return coords[0] > sw_lon and coords[0] < ne_lon and coords[1] > sw_lat and coords[1] < ne_lat
