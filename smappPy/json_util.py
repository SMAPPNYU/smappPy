"""
JSON utilities for MongoDB and twitter applications

Created by dpb on 8/21/2013
"""

import re
import simplejson as json

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

class ConcatJSONDecoder(json.JSONDecoder):
    """
    A class to retrive json objects from stream with multiple objects. Handles the decoding of
    multiple objects via the default JSONDecoder object's raw_decode method (returns json object
    in python object form and the end index of that object in the stream).
    See docs: http://simplejson.googlecode.com/svn/tags/simplejson-2.1.1/docs/index.html
    Returns a list of python objects representing the json objects in the stream.
    """
    def decode(self, s, _w=WHITESPACE.match):
        s_len = len(s)

        objs = []
        end = 0 
        while end != s_len:
            obj, end = self.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            objs.append(obj)
        return objs

