"""
Cursors for easier pagination using the facebook-sdk library
"""

import calendar
import requests
from dateutil import parser

class TimeBasedPaginationCursor:
    """
    Cursor for handling Facebook GraphAPI Time-based paged items (such as posts).
    Time-based pagination works backwards:
      - the first page hit will contain the newest posts
      - the 'next' page is the chronologically previous page (older posts)


    Example:
    --------
    first_page = graph.get_connections('user-alias', 'posts', since=xxxx, until=yyyy)
    c = TimeBasedPaginationCursor(first_page, since=xxxx)
    all_posts = c.items()
    """
    def __init__(self, response, since=0, debug=False, num_retries=10):
        self.response = response
        self.since = since
        self.debug = debug
        self.num_retries = num_retries

    def _unix_timestamp_from_isoformat_string(self, timestring):
        return calendar.timegm(parser.parse(timestring).timetuple())

    def items(self):
        """
        Returns all items from all subsequent pages fitting the since criterium.
        """
        data = list()
        response = self.response
        latest_timestamp_in_response = self._unix_timestamp_from_isoformat_string(response['data'][0]['created_time'])
        while latest_timestamp_in_response > self.since:
            data_in_range = [d for d in response['data']
                if self._unix_timestamp_from_isoformat_string(d['created_time']) > self.since]
            data += data_in_range
            if len(data_in_range) < len(response['data']):
                break
            if self.debug:
                print("TimeBasedPaginationCursor: requesting: {}".format(response['paging']['next']))

            i = 0
            while i < self.num_retries:
                response = requests.get(response['paging']['next']).json()
                if response.ok:
                    break
                else:
                    if self.debug:
                        print("Error:")
                        print(response)
                        print(response.text)
                        print("retrying..{}".format(i))
                i += 1

            if response.ok:
                latest_timestamp_in_response = self._unix_timestamp_from_isoformat_string(response['data'][0]['created_time'])
        return data

