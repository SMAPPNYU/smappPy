"""
Twitter OAuth utilities for python

@auth dpb
@date 12/02/2013
"""

class AuthCheckException(Exception):
    """
    Define a custom exception for Auth checking
    """
    pass

def tweepy_auth(filename):
    """Create and return a tweepy.OAuthHandler object from a file containing oauth fields"""
    import tweepy
    oauth_dict = read_oauth(filename)
    auth = tweepy.OAuthHandler(oauth_dict["consumer_key"], oauth_dict["consumer_secret"])
    auth.set_access_token(oauth_dict["access_token"], oauth_dict["access_token_secret"])
    return auth

def read_oauth(filename):
    """Reads in a json dict Oath object. Exception if invalid"""
    import simplejson as json
    oauth = json.loads(open(filename, 'r').read())
    check_oauth(oauth)
    return oauth

def check_oauth(oauth_dict):
    """
    Checks that the four required values (consumer_key, consumer_secret, access_token, and 
    access_token_secret) are in the given dict
    """
    if "consumer_key" not in oauth_dict or oauth_dict["consumer_key"] == "":
        raise AuthCheckException("Authentication error: Failed to provide consumer_key")
    elif "consumer_secret" not in oauth_dict or oauth_dict["consumer_secret"] == "":
        raise AuthCheckException("Authentication error: Failed to provide consumer_secret")
    elif "access_token" not in oauth_dict or oauth_dict["access_token"] == "":
        raise AuthCheckException("Authentication error: Failed to provide access_token")
    elif "access_token_secret" not in oauth_dict or oauth_dict["access_token_secret"] == "":
        raise AuthCheckException("Authentication error: Failed to provide access_token_secret")


