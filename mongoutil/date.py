"""
datetime.py contains datetime utilities and functionality for twitter and mongodb

Created by dpb on 8/21/2013
"""


mongo_date_format = "%a %b %d %H:%M:%S +0000 %Y"

def mongodate_to_datetime(mongodate):
    """Takes a Mongo/BSON-format date string, returns a corresponding python datetime object"""
    from datetime import datetime
    return datetime.strptime(mongodate, mongo_date_format)

