"""
Functions for getting tweets from Twitter (via REST API), file, and database

@auth dpb
@date 2/24/2014
"""

def keyword_tweets():
    """"""
    pass

def user_tweets():
    """"""
    pass

def geo_tweets():
    """"""
    pass

def tweets_from_file(tweetfile):
    """
    Returns a list of tweets read from given file. Tweets are dicts representing json of 
    file contents. For a less-memory intensive version, consider the tweet_from_file_IT() 
    function.
    Note: will not check validity of tweet. Will simply return dict representations of
    JSON entities in the file
    """
    from bson.json_util import loads
    from json_util import ConcatJSONDecoder

    with open(tweetfile) as handle:
        tweets = loads(handle.read(), cls=ConcatJSONDecoder)
    return tweets

def tweets_from_file_IT(tweetfile):
    """
    Returns an iterator for tweets in given tweetfile. Tweets are considered dict
    representations of JSON in given tweetfile
    """
    from bson.json_util import loads
    
    with open(tweetfile) as handle:
        for line in handle:
            yield loads(line.strip())

def tweets_from_db():
    """"""
    pass
