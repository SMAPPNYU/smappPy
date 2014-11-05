"""
Utilities for images

@auth dpb
@date 2/19/2014
"""

import imghdr
import urllib
from smappPy.entities import contains_image, get_image_urls

class EmptyImageException(Exception):
    """Custom exception for case when image read from URL is 0 bytes/empty"""
    pass

class ImageFormatException(Exception):
    """Custom exception for case when image type not understood by imghdr"""
    pass


def save_web_image(url, filename):
    """Attempts to get image from url, stores it in file. Throws exceptions directly
    from urllib functions (urlretrieve)"""
    
    url_contents = urllib.urlopen(url).read()
    if len(url_contents) < 1:
        raise EmptyImageException("URL '{0}' returned empty file")
    
    img_type = imghdr.what(None, h=url_contents)
    if not img_type:
        raise ImageFormatException("imghdr failed to type image at {0}".format(url))
    filename += ".{0}".format(img_type)

    with open(filename, "wb") as handle:    
        handle.write(url_contents)

def get_image_occurrences(tweets):
    """Takes a cursor (or any iterable) of tweets, returns a sorted list of
    (url, num_occurrences) pairs (sorted by num_occurrences, greatest first) of all 
    images in the tweets given"""
    url_count = {}
    for tweet in tweets:
        if contains_image(tweet):
            urls = get_image_urls(tweet)
            for url in urls:
                if url in url_count:
                    url_count[url] += 1
                else:
                    url_count[url] = 1
    url_pairs = url_count.items()
    url_pairs.sort(key=lambda p: p[1], reverse=True)
    return url_pairs

