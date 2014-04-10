"""
Contains smappPy functionality for storing tweets to file, database, etc

@auth dpb
@date 2/24/2014
"""

def tweets_to_file(tweets, tweetfile, append=False, pure_json=False, pretty=False):
    """
    Exports a collection (iterable) of tweets to given file. Exports tweets in mongoDB
    extended special bson format. 
    To append to given tweetfile, pass append=True
    For pure json (not bson object rep), pass pure_json=True. 
    To pretty-print json (value-per-line and spacing), pass pretty=True
    """
    if pure_json:
        from simplejson import dumps
    else:
        from bson.json_util import dumps
    if append:
        handle = open(tweetfile, "a")
    else:
        handle = open(tweetfile, "w")
    if pretty:
        for tweet in tweets:
            handle.write(dumps(tweet, indent=4, separators=(',', ': ')) + "\n")
    else:
        for tweet in tweets:
            handle.write(dumps(tweet) + "\n")
    handle.close()


def tweets_to_db(server, port, user, password, database, collection, tweets):
    """"""
    pass

