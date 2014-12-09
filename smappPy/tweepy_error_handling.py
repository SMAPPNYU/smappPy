"""
Twitter error handling functions
"""

import json
from ssl import SSLError
from httplib import IncompleteRead
from tweepy.error import TweepError

# Examples of crazy shit I'm seeing:
# user_timeline endpoint:
#{'errors': [{'message': 'Rate limit exceeded', 'code': 88}]}
# 
# friends_ids and followers_ids endpoints    
#[{'message': 'Rate limit exceeded', 'code': 88}]

#[{u'message': u'Rate limit exceeded', u'code': 88}]

def parse_tweepy_error(error):
    """
    Takes instance of tweepy.error.TweepError. Tries to figure out what the hell
    is going on with it, due to Twitter's bizarre and inconsistent error 
    formatting.
    Returns (Gauranteed! Right? Because we're not asses!) a dict in the form:
    {
        "code": <int>ErrorCode}, 
        "message": <str>"Some descriptive message"
    }
    """
    code, message = 1, str(error)

    try:
        e = json.loads(error.message)
    except:
        e = error.message

    if isinstance(e, dict):
        if "errors" in e:
            if len(e["errors"]) > 0:
                try:
                    code = e["errors"][0]["code"]
                    message = e["errors"][0]["message"]
                except:
                    pass
    elif isinstance(e, list):
        if len(e) > 0:
            try:
                code = e[0]["code"]
                message = e[0]["message"]
            except:
                pass

    return {"code": code, "message": message}


def call_with_error_handling(function, *args, **kwargs):
    """
    Calls given functions with given arguments, wrapping function call in
    try-except block catching most twitter errors and responses.
    Returns tuple: (function return value, return code). Return code is 0
    when function executes successfully. Custom Error Codes:
        1   - Unknown/Unparseable Twitter error
        2   - HTTPLib incomplete read error
        3   - SSL Read timeout error
        4   - ValeError (eg: "No JSON object could be decoded")
    """
    #TODO: Extend to consider as many twitter error codes as you have patience for
    #TODO: (https://dev.twitter.com/docs/error-codes-responses)
    try:
       ret = function(*args, **kwargs)
    except TweepError as e:
        error_dict = parse_tweepy_error(e)
        print ".. Error {0}: {1}".format(error_dict["code"], error_dict["message"])
        return (None, error_dict["code"])
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



