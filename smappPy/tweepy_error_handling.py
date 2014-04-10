"""
Twitter error handling functions
"""

from tweepy.error import TweepError

def call_with_error_handling(function, *args, **kwargs):
    """
    Calls given functions with given arguments, wrapping function call in
    try-except block catching most twitter errors and responses.
    Returns tuple: (function return value, return code). Return code is 0
    when function executes successfully.
    """
    #TODO: Extend to consider as many twitter error codes as you have patience for
    #TODO: (https://dev.twitter.com/docs/error-codes-responses)
    try:
       ret = function(*args, **kwargs)
    except TweepError as e:
        if type(e.message) == list and len(e.message) > 0:
            if e.message[0]["code"] == 34:
                print ".. No user found with ID"
            elif e.message[0]["code"] == 63:
                print ".. User's account has been suspended"
            elif e.message[0]["code"] == 88:
                print ".. Rate limit exceeded"
            elif e.message[0]["code"] == 130:
                print ".. Twitter over capactity (130)"
            elif e.message[0]["code"] == 131:
                print ".. Unknown internal twitter error (131)"
            return (None, e.message[0]["code"])
        elif type(e.message) in [str, unicode]:
            print ".. Error: {0}".format(e)
            return (None, 1)
        raise(e)

    return (ret, 0)