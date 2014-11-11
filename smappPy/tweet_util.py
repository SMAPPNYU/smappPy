"""
Utility functions for tweets
"""

import random
from smappPy.date import mongodate_to_datetime
from smappPy.entities import contains_entities

ID_FIELD = "id"
RANDOM_FIELD = "random_number"
TIMESTAMP_FIELD = "timestamp"

def add_random_to_tweet(tweet):
    """Takes a tweet dict, adds a random number field to it via python random module"""
    # If already defined, do nothing
    if RANDOM_FIELD in tweet and tweet[RANDOM_FIELD] != None:
        return
    tweet[RANDOM_FIELD] = random.random()

def add_timestamp_to_tweet(tweet):
    """Takes a tweet dict, adds a native datetime object corresponding to tweet's 'created_at' field"""
    # If already defined, do nothing
    if TIMESTAMP_FIELD in tweet and tweet[TIMESTAMP_FIELD] != None:
        return
    if 'created_at' not in tweet:
        raise Exception("Tweet (id_str: {0}) has no 'created_at' field".format(tweet['id_str']))
    tweet[TIMESTAMP_FIELD] = mongodate_to_datetime(tweet['created_at'])


# Note: All 'id_str' fields are ignored in favor of 'id' long-int fields
# Note: All '_https' fields are ignored in favor of '_http' fields

# Tweet fields skipped: annotations, current_user_retweet, favorited, geo (deprecated),
# scopes, retweeted, 
#
# Tweet fields to link to other objects: retweeted_status_id, user_id, 
#
#TODO: 'withheld_in_countries' is a list in Tweets (string in User).
#TODO: join it into a string for this field

tweet_fields = ["id", "created_at", "has_entities",
                "coord_long", "coord_lat", "coord_type",  
                "favorite_count", "filter_level", 
                "in_reply_to_screen_name", "in_reply_to_status_id", "in_reply_to_user_id", 
                "lang", "possibly_sensitive", "retweet_count",
                "retweeted_status_id", "source", "text",
                "truncated", "user_id", "withheld_copyright",
                "withheld_in_countries", "withheld_scope"]

# User skipped fields: follow_request_sent, following, profile_background_image_url_https, 
# profile_image_url_https, profile_background_color, profile_background_tile, profile_link_color,
# profile_sidebar_border_color, profile_sidebar_fill_color, profile_text_color,
# profile_use_background_image, show_all_inline_media
#
# User fields to link to other objects: status_id, 
#
#TODO: User entities - how to deal with? Separate tables? Or same tables (hashtag, media, url)
#TODO: but with general ID reference? Or tweet + user id fields?

user_fields = ["id", "contributors_enabled", "created_at", 
               "default_profile", "default_profile_image", "description",
               "favourites_count", "followers_count", "friends_count",
               "geo_enabled", "is_translator", "lang",
               "listed_count", "location", "name",
               "notifications", "profile_background_image_url",
               "profile_banner_url", "profile_image_url", "protected",
               "screen_name", "status_id", "statuses_count", 
               "time_zone", "url", "utc_offset", 
               "verified", "withheld_in_countries", "withheld_scope"]

hashtag_fields = ["index_first", "index_last", "text",
                  "tweet_id"]

media_fields = ["id", "type", "index_first", "index_last", 
                "url", "media_url", "display_url", 
                "expanded_url", "tweet_id"]

url_fields = ["index_first", "index_last", "url",
              "display_url", "expanded_url", "tweet_id"]

user_mentions_fields = ["id", "index_first", "index_last"
                        "name", "screen_name", "tweet_id"]

place_fields = ["country", "country_code", "full_name", 
                "name", "place_type", "url", 
                "coord_sw_long", "coord_sw_lat", "coord_se_long", "coord_se_lat", 
                "coord_ne_long", "coord_ne_lat", "coord_nw_long", "coord_nw_lat",
                "tweet_id"]

contributors_fields = ["id", "screen_name", "tweet_id"]


def flatten_tweet(tweet, user_row=True, entity_rows=True, place_row=False, contributor_rows=False):
    """
    Takes a tweet and returns a dict of label => list-of-lists representing the tweet, "flattened"
    into a relational DB-like scheme (or suitable for CSVs).
    Row elements correspond to header lists above this function.
    Tweet should be a dict representing Twitter's 'status'/'tweet' object: 
    https://dev.twitter.com/overview/api/tweets
    """
    flat_rows = {
        "tweet_row": [],
        "user_row": [],
        "hashtag_rows": [],
        "media_rows": [],
        "url_rows": [],
        "user_mention_rows": [],
        "place_row": [],
        "contributor_rows" = [],
    }

    # Build tweet row
    tweet_row = [tweet["id"], tweet["created_at"], contains_entities(tweet)]
    if tweet["coordinates"]:
        tweet_row.append(tweet["coordinates"]["coordinates"][0])
        tweet_row.append(tweet["coordinates"]["coordinates"][1])
        tweet_row.append(tweet["coordinates"]["type"])
    else:
        tweet_row += [None, None, None]
    tweet_row


tweet_fields = ["id", "created_at", "has_entities",
                "coord_long", "coord_lat", "coord_type",  
                "favorite_count", "filter_level", 
                "in_reply_to_screen_name", "in_reply_to_status_id", "in_reply_to_user_id", 
                "lang", "possibly_sensitive", "retweet_count",
                "retweeted_status_id", "source", "text",
                "truncated", "user_id", "withheld_copyright",
                "withheld_in_countries", "withheld_scope"]








