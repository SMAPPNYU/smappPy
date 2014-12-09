"""
Twitter error handling functions
"""

import simplejson as json
from ssl import SSLError
from httplib import IncompleteRead
from tweepy.error import TweepError

def call_with_error_handling(function, *args, **kwargs):
    """
    Calls given functions with given arguments, wrapping function call in
    try-except block catching most twitter errors and responses.
    Returns tuple: (function return value, return code). Return code is 0
    when function executes successfully. Custom Error Codes:
        1   - Unknown Twitter error
        2   - HTTPLib incomplete read error
        3   - SSL Read timeout error
        4   - ValeError (eg: "No JSON object could be decoded")
    """
    #TODO: Extend to consider as many twitter error codes as you have patience for
    #TODO: (https://dev.twitter.com/docs/error-codes-responses)
    try:
       ret = function(*args, **kwargs)
    except TweepError as e:
        try:
            error_json = json.loads(e.message)
        except:
            print ".. Error (failed to load JSON): {0}".format(e)
            return (None, 1)
        if "errors" in error_json and len(error_json["errors"]) > 0:
            if error_json["errors"][0]["code"] == 34:
                print ".. No user found with ID"
            elif error_json["errors"][0]["code"] == 63:
                print ".. User's account has been suspended"
            elif error_json["errors"][0]["code"] == 88:
                print ".. Rate limit exceeded"
            elif error_json["errors"][0]["code"] == 130:
                print ".. Twitter over capactity (130)"
            elif error_json["errors"][0]["code"] == 131:
                print ".. Unknown internal twitter error (131)"
            return (None, error_json["errors"][0]["code"])
        else:
            print ".. Error (JSON in unexpected format): {0}".format(e)
            return (None, 1)
    except IncompleteRead as i:
        print ".. HTTPLib incomplete read error: {0}".format(i)
        return (None, 2)
    except SSLError as s:
        print ".. SSL read timeout error: {0}".format(s)
        return (None, 3)
    except ValueError as v:
        print ".. Value error (most likely JSON problem): {0}".format(v)
        return (None, 4)

    return (ret, 0)

    #[{'message': 'Rate limit exceeded', 'code': 88}]