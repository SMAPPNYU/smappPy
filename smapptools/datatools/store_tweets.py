"""
Contains smappPy functionality for storing tweets to file, database, etc

@auth dpb
@date 2/24/2014
"""

from simplejson import dumps as json_dumps
from bson.json_util import dumps as bson_dumps

def tweets_to_file(tweets, tweetfile, append=False, pure_json=False, pretty=False):
    """
    Exports a collection (iterable) of tweets to given file. Exports tweets in mongoDB
    extended special bson format. 
    To append to given tweetfile, pass append=True
    For pure json (not bson object rep), pass pure_json=True. 
    To pretty-print json (value-per-line and spacing), pass pretty=True
    """
    raise DeprecationWarning(
        "'tweets_to_file' is deprecated. Use 'tweets_to_bson' or 'tweets_to_json' instead.")
    return

def tweets_to_bson(tweets, tweetfile, append=False):
    """
    Exports a collection of tweets (any iterable of tweet objects) to given
    file in MongoDB's native BSON format. Not line-separated.
    To append to given filename, pass append=True
    """
    if append:
        handle = open(tweetfile, "ab+")
    else:
        handle = open(tweetfile, "wb")
    for tweet in tweets:
        handle.write(bson_dumps(tweet))
    handle.close()

def tweets_to_json(tweets, tweetfile, append=False, pretty=False):
    """
    Exports a collection of tweets (any iterable of tweet objects) to given
    file in JSON, line-separated format.
    To append to given filename, pass append=True
    To print in pretty (line- and entity-separated) format, pass pretty=True
    """
    if append:
        handle = open(tweetfile, "a")
    else:
        handle = open(tweetfile, "w")
    if pretty:
        for tweet in tweets:
            handle.write(json_dumps(tweet, indent=4, separators=(',', ': ')) + "\n")
    else:
        for tweet in tweets:
            handle.write(json_dumps(tweet) + "\n")
    handle.close()

def tweets_to_db(server, port, user, password, database, collection, tweets):
    """"""
    raise NotImplementedError("Not yet implemented")

