"""
Contains functions for building text files containing documents
for eventual topic modeling.
"""

from smappPy.MT import is_MT
from smappPy.retweet import is_retweet
from smappPy.text_clean import clean_whitespace
from smappPy.entities import remove_entities_from_text


COUNTER = 10000


def build_tweet_user_docs(collection, outhandle, remove_hashtags, remove_mentions, 
        remove_RTs, remove_MTs, start=None, end=None):
    """
    Same as below, but compiles docs per user, so writes line-per-user
    content to given outhandle.
    Can still paramterize by time (start and end for query. If none, ignored)
    """
    #BEWARE: Potentially mega memory heavy, unless do via a pre-computed list of
    # user IDs (can't just drag in all tweets and store all user docs for big
    # collections). Could get unique UserIDs, then query for user tweets, and so
    # build and write a doc at a time.
    raise NotImplementedError


def build_tweet_time_docs(collection, outhandle, start, num_periods, time_step, 
        remove_hashtags, remove_mentions, remove_RTs, remove_MTs):
    """
    Queries for tweets from given collection, writes all tweet text
    with cleaned entities to outfile, in line-per-timestep format.
    Queries tweets in range 'start' to 'start' + 'num_periods' * 'time_step'
    """
    for period in [start + (time_step * x) for x in range(num_periods)]:
        print "Processing {0}".format(period)
        
        tweets = collection.find({"timestamp": {"$gte": period, "$lt": period + time_step}})
        tweet_count = tweets.count(with_limit_and_skip=True)
        count = 0
        
        for tweet in tweets:
            if count % COUNTER == 0:
                print ".. tweet {0} of {1}".format(count, tweet_count)
            count += 1

            if remove_RTs:
                if is_retweet(tweet):
                    continue
            if remove_MTs:
                if is_MT(tweet):
                    continue
            
            clean_text = remove_entities_from_text(tweet, 
                                                   remove_hashtags=remove_hashtags, 
                                                   remove_mentions=remove_mentions)

            # Basic cleaning: normalize whitespace
            clean_text = clean_whitespace(clean_text)

            outhandle.write("{0} ".format(clean_text.encode("utf8")))
        outhandle.write("\n")
    print "Writing tweet text to '{0}' Complete".format(outhandle.name)
