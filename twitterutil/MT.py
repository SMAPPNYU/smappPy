"""
Functions to deal with "modified tweets" (MTs) from twitter

@auth dpb
@date 2/11/2014
"""

import re

mt_initial_pattern = r"^MT @"
mt_interior_pattern = r" MT @"

def is_MT(tweet):
    """"""
    if re.search(mt_interior_pattern, tweet['text'].encode('utf-8')):
        return True
    elif re.search(mt_initial_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def is_initial_MT(tweet):
    """"""
    if re.search(mt_initial_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def is_interior_MT(tweet):
    """"""
    if re.search(mt_interior_pattern, tweet['text'].encode('utf-8')):
        return True
    return False

def split_MT(tweet):
    """
    Splits a normal-form MT into three parts: prefix (usually commentary), user listed in
    the MT, and postfix (usually the original tweet that was MTed)
    Returns a tuple, elements may be empty strings ("") or None
    """
    if not is_MT(tweet):
        print "Warning: given tweet is not a modified tweet (as far as we can tell)"
        return

    mt_pattern = r"(?P<prefix>.*?)\s?MT @(?P<user>.*?)[:\s]+(?P<postfix>.*)"
    match = re.match(mt_pattern, tweet['text'].encode('utf-8'))

    if match == None:
        raise Exception("Could not match MT structure (text: {0})".format(tweet['text']))
    return (match.group("prefix"), match.group("user"), match.group("postfix"))


