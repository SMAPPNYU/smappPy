"""
JSON utilities for MongoDB and twitter applications

Created by dpb on 8/21/2013
"""

import re
import simplejson as json
from simplejson import JSONDecodeError

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


class StreamJsonListLoader():
    """
    When you have a big JSON file containint a list, such as

    [{
        ...
    },
    {
        ...
    },
    {
        ...
    },
    ...
    ]

    And it's too big to be practically loaded into memory and parsed by json.load,
    This class comes to the rescue. It lets you lazy-load the large json list.
    """

    def __init__(self, filename_or_stream):
        if type(filename_or_stream) == str:
            self.stream = open(filename_or_stream)
        else:
            self.stream = filename_or_stream

        if not self.stream.read(1) == '[':
            raise NotImplementedError('Only JSON-streams of lists (that start with a [) are supported.')

    def __iter__(self):
        return self

    def next(self):
        read_buffer = self.stream.read(1)
        while True:
            try:
                json_obj = json.loads(read_buffer)

                if not self.stream.read(1) in [',',']']:
                    raise Exception('JSON seems to be malformed: object is not followed by comma (,) or end of list (]).')
                return json_obj
            except JSONDecodeError:
                next_char = self.stream.read(1)
                read_buffer += next_char
                while next_char != '}':
                    next_char = self.stream.read(1)
                    if next_char == '':
                        raise StopIteration
                    read_buffer += next_char
class NonListStreamJsonListLoader():
    """
    When you have a big JSON file containint a list, such as

    {
        ...
    }
    {
        ...
    }
    {
        ...
    }


    And it's too big to be practically loaded into memory and parsed by json.load,
    This class comes to the rescue. It lets you lazy-load the large json list.

    What differentiates this from the StreamJsonListLoader class is that the former has a proper
    JSON list, and this just has one JSON object per line, without surrounding []
    and delimiting commas.
    """

    def __init__(self, filename_or_stream):
        if type(filename_or_stream) == str:
            self.stream = open(filename_or_stream)
        else:
            self.stream = filename_or_stream

    def __iter__(self):
        return self

    def next(self):
        read_buffer = self.stream.read(1)
        while True:
            try:
                json_obj = json.loads(read_buffer)
                return json_obj
            except JSONDecodeError:
                next_char = self.stream.read(1)
                read_buffer += next_char
                while next_char != '}':
                    next_char = self.stream.read(1)
                    if next_char == '':
                        raise StopIteration
                    read_buffer += next_char
