"""
Utility to filter a bson file of tweets and output a bson file with only tweets from a certain date.

@jonathanronen 3/2015
"""

import pytz
import argparse
from datetime import datetime
from bson import BSON, decode_file_iter

MONTHS={
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
}

def parsedate(s):
    t = s.split()
    tt = t[3].split(":")
    if t[4] != "+0000":
        raise "Only works for utc"
    return datetime(int(t[-1]), MONTHS[t[1]], int(t[2]), int(tt[0]), int(tt[1]), int(tt[2])).replace(tzinfo=pytz.utc)

def tweet_date(tweet):
    """
    Returns tweet date. Compatible with tweet documents which have a 'timestamp' field
    as well as older ones that don't.
    """
    if 'timestamp' in tweet:
        return tweet['timestamp']
    return parsedate(tweet['created_at'])

def filter_records(infile, year, month, day, tz):
    """
    Takes in a file handle pointing at a BSON file, and a year, month, day, timezone.
    Returns only those tweets which were sent on that date in that timezone.
    """
    it = decode_file_iter(infile)
    try:
        for rec in it:
            d = tweet_date(rec).astimezone(tz)
            if d.year == year and d.month == month and d.day == day:
                yield rec
    except Exception as e:
        print e

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--input-file', required=True, help='BSON file to read from')
    arg_parser.add_argument('-o', '--output-file', required=True, help='BSON file to dump to')
    arg_parser.add_argument('-y', '--year', type=int, required=True, help='year')
    arg_parser.add_argument('-m', '--month', type=int, required=True, help='month')
    arg_parser.add_argument('-d', '--day', type=int, required=True, help='day')
    arg_parser.add_argument('-z', '--timezone', default='America/New_York', help="Effective time zone name [America/New_York]")

    args = arg_parser.parse_args()

    print("Filtering for tweets sent on {year}/{month}/{day} in {tz}".format(
        year=args.year,
        month=args.month,
        day=args.day,
        tz=args.timezone))

    with open(args.input_file, 'rb') as infile:
        with open(args.output_file, 'wb') as outfile:
            tzinfo = pytz.timezone(args.timezone)
            outfile.writelines(BSON.encode(e) for e in filter_records(infile, args.year, args.month, args.day, tzinfo))
    print "Done."