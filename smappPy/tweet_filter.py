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

    Example:
    ========
    field_contains(tweet, 'user.screen_name', 'obama', 'putin')
    # true if the user's handle contains 'obama' or 'putin'
    """
    path = field.split('.')
    value = tweet[path.pop(0)]
    for p in path:
        value = value[p]
    value = value.lower()
    return any(term.lower() in value for term in terms)

def user_location_contains(tweet, *terms):
    """
    True if tweet['user']['location'] contains any of the terms.
    """
    return field_contains(tweet, 'user.location', *terms)

def user_description_contains(tweet, *terms):
    """
    True if tweet['user']['description'] contains any of the terms.
    """
    return field_contains(tweet, 'user.description', *terms)

def within_geobox(tweet, sw_lon, sw_lat, ne_lon, ne_lat):
    """
    True if tweet is geotagged and is sent within the box specified by GeoJSON points (longitude, latitude)
    (sw_lon, sw_lat)  <-  the southwest corner
    (ne_lon, ne_lat)  <-  the northeast corner

    Example:
    ========
    within_geobox(tweet, -75.280303,39.8670041,-74.9557629,40.1379919)
    # true for tweets tweeted within a box surrounding Philadelphia
    """
    if 'coordinates' not in tweet or 'coordinates' not in tweet['coordinates']:
        return False
    coords = tweet['coordinates']['coordinates']
    return coords[0] > float(sw_lon) and coords[0] < float(ne_lon) and coords[1] > float(sw_lat) and coords[1] < float(ne_lat)

def place_name_contains(tweet, *terms):
    """
    True if the `place` associated with the tweet contains any of the terms
    For more information about `place see https://dev.twitter.com/overview/api/places

    Example:
    ========
    place_name_contains(tweet, 'Kiev')
    # true for tweets where tweet['place']['full_name'] contains 'kiev'.
    """
    if 'place' not in tweet or tweet['place'] is None:
        return False
    return field_contains(tweet, 'place.full_name', *terms)
