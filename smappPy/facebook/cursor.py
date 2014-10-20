"""
Cursors for easier pagination using the facebook-sdk library
"""

import time
import logging
import calendar
import requests
from dateutil import parser

def _call_with_retries(method, *args, **kwargs):
    """
    Call graph API method with `n_retries` retries, waiting `t_wait` seconds
    between each call.
    If the call still fails after `n_retries`, raises whatever exception.

    Usage example:
    _call_with_retries(graph.get_connections('me', 'posts'), since=0, until=12345, n_retries=3, t_wait=0.5,)
    """
    n_retries = kwargs.pop('n_retries', 10)
    t_wait    = kwargs.pop('t_wait', 1)

    for trial in range(n_retries):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            logging.warn(e)
        time.sleep(t_wait)
    raise e

def _grab_next_page(page):
    """
    `page` is a facebook graph result page, so it has a key 'paging' where
    'next' is an http link to the next page, with all neccesary params

    This method calls that next page, and raises an exception if the response is
    not 200.

    If ok, returns JSON.
    """
    response = requests.get(page['paging']['next'])
    if not response.ok:
        raise Exception(response.status_code, response.text)
    return response.json()

def _unix_timestamp_from_isoformat_string(timestring):
    return calendar.timegm(parser.parse(timestring).timetuple())


def _object_created_since(since):
    def checker(o):
        return _unix_timestamp_from_isoformat_string(o['created_time']) >= since
    return checker

class Cursor:
    """
    Base class for cursoring through facebook's graph's paged things.
    """
    def __init__(self, method, *args, **kwargs):
        self._method = method
        self._args = args
        self._kwargs = kwargs

        # Currently only supports time-based pagination
        if 'since' in kwargs:
            self._continue_criterion = _object_created_since(kwargs['since'])
        elif 'before' in kwargs or 'after' in kwargs:
            raise NotImplementedError('cursor-based paging not implemented')
        elif 'offset' in kwargs:
            raise NotImplementedError('offset-based paging not implemented')
        else:
            self._continue_criterion = lambda o: True

    def __iter__(self):
        self.current = _call_with_retries(self._method, *self._args, **self._kwargs)
        return self

    def next(self):
        if len(self.current['data']) < 1:
            self.current = _call_with_retries(_grab_next_page, self.current)
            if len(self.current['data']) < 1:
                raise StopIteration
        if self._continue_criterion(self.current['data'][0]):
            return self.current['data'].pop(0)
        raise StopIteration
