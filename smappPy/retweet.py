"""
A module containing python utilities regarding retweets (such as is_retweet)

@auth dpb
@date 10/25/2013
"""

# Define manual retweet patterns
rt_manual_pattern = r"^RT @"
rt_partial_pattern = r" RT @"


def is_retweet(tweet):
    """Takes a python-native tweet obect (a dict). Returns True if a tweet is any kind of retweet"""
    import re
    if 'retweeted_status' in tweet and tweet['retweeted_status']:
        return True
    elif re.search(rt_manual_pattern, tweet['text'].encode('utf-8')):
        return True
    elif re.search(rt_partial_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def is_official_retweet(tweet):
    """Same as above, except only checks for official retweet"""
    if 'retweeted_status' in tweet:
        return True
    return False

def is_manual_retweet(tweet):
    """Same as above, except checks for both types of manual retweet"""
    import re
    if re.search(rt_manual_pattern, tweet['text'].encode('utf-8')):
        return True
    elif re.search(rt_partial_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def is_partial_retweet(tweet):
    """Same as above, except checks for only the partial (non-initial) type of manual retweet"""
    import re
    if re.search(rt_partial_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def get_user_retweeted(tweet, warn=True):
    """
    Given a tweet that is a retweet, return a tuple of (user ID, user screen_name) representing the
    user that is retweeted (the author of the original tweet).

    Set warn parameter to False to avoid printing warning messages on passing non-RTs.

    Note: user ID will be None in the case of manual retweets. Always check for this.
    
    Note: For tweets with nested retweets (multiple manual retweets in the tweet text), this will only
    return the FIRST retweeted user.
    """
    import re

    if not is_retweet(tweet):
        if warn:
            print "Warning: given tweet is not a retweet (as far as we can tell)"
        return

    if is_official_retweet(tweet):
        return (tweet['retweeted_status']['user']['id'], tweet['retweeted_status']['user']['screen_name'])

    elif is_manual_retweet(tweet):
        components = split_manual_retweet(tweet)
        if components == None or components[1] == None:
            print "Warning: could not find user information in manual retweet (text: {0})".format(tweet['text'])
            return
        return (None, components[1])

def split_manual_retweet(tweet):
    """
    Takes a tweet (checks if it is a manual retweet), and returns a triple: 
        (prefix, user screen_name, postfix),
    where prefix and postfix are the text before and after the RT @USER tag, and user screen_name 
    is the user targeted in the retweet (the USER in RT @USER).
    Note: The prefix is potentially empty, if the RT occurs at the very beginning of the tweet text.
    Note: If the retweet is a manual nested retweet (contains more than one RT @ tag), this will
    split the tweet based on the first-encountered manual tweet tag.
    """
    import re
    if not is_manual_retweet(tweet):
        print "Warning: given tweet is not a manual retweet (as far as we can tell)"
        return

    rt_pattern = r"(?P<prefix>.*?)\s?RT @(?P<user>.*?)[:\s]+(?P<postfix>.*)"
    rt_re = re.compile(rt_pattern, re.U|re.DOTALL)
    match = rt_re.match(tweet['text'])

    if match == None:
        raise Exception("Could not match Manual Retweet structure (text: {0})".format(
            tweet["text"].encode("utf8")))
    return match.groups()


