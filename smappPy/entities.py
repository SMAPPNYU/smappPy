"""
Functions and data for Tweet "entities" field and component parts.

@auth dpb
@date 1/14/2014, 2/11/2014

Tweet "entities":
    urls: []
    media: []
    symbols: []
    hashtags: []
    user_mentions: []

media:
    id: <int>                               // ID of the media object
    id_str: <str>
    media_url: <str>
    media_url_https: <str>
    url: <str>
    display_url: <str>
    expanded:url: <str>
    sizes: {
        thumb:  {w: 150, h: 150, resize: crop}
        small:  {w: 340, h: 226, resize: fit}
        medium: {w: 600, h: 399, resize: fit}
        large:  {w: 800, h: 532, resize: fit}
    }
    type: "photo"                           // So far, only "photo"
    indices: [<start-index>, <stop-index>]  // start-index is 0-based first char of URL
                                            // stop-index is 1 + 0-based last char of URL
urls:
    url: <str>
    display_url: <str>
    expanded_url: <str>                     // The resolved URL
    indices: [<start_incl>, <stop_excl>]

user_mentions:
    id: <int>                               // Mentioned user's data
    id_str: <str>
    screen_name: <str>
    name: <str>
    indices: [<start_incl>, <stop_excl>]    // Indices include '@' symbol

hashtags:
    text: <str>                             // WITHOUT the '#' char
    indices: [<start_incl, stop_excl>]      // Indices include '#' symbol

symbols:
    text: <str>                             // WITHOUT the '$' char
    indices: [<start_incl>, <stop_excl>]    // Indices include '$' symbol
"""

import re

# General functions
def contains_entities(tweet):
    """
    Returns True if tweet contains one or more entities (hashtag, url, or media)
    """
    if "entities" not in tweet:
        return False
    if "hashtags" in tweet["entities"] and len(tweet["entities"]["hashtags"]) > 0:
        return True
    if "media" in tweet["entities"] and len(tweet["entities"]["media"]) > 0:
        return True
    if "urls" in tweet["entities"] and len(tweet["entities"]["urls"]) > 0:
        return True
    if "user_mentions" in tweet["entities"] and len(tweet["entities"]["user_mentions"]) > 0:
        return True
    return False

def remove_entities_from_text(tweet, text=None, remove_hashtags=True, remove_mentions=True):
    """
    Removes all entity text from tweets using entity indices, not text matching.
    Note: 'text' parameter must match indices of tweet entities (ie, text should be 
    either the full tweet text OR a substring starting at the beginning of
    the original tweet text OR a substring padded by arbitrary characters so that
    the indices of the substring align with the original tweet text)
    """
    if "entities" not in tweet:
        return tweet["text"]

    # Create list representation of text to clean
    if text:
        text_list = list(text)
    else:
        text_list = list(tweet["text"])

    # Go through all entities, replacing text_list entries at entity indices with None
    if "urls" in tweet["entities"]:
        for u in tweet["entities"]["urls"]:
            l_index, r_index = u["indices"][0], u["indices"][1]
            text_list[l_index:r_index] = [None] * (r_index - l_index)
    if "media" in tweet["entities"]:
        for m in tweet["entities"]["media"]:
            l_index, r_index = m["indices"][0], m["indices"][1]
            text_list[l_index:r_index] = [None] * (r_index - l_index)
    if "symbols" in tweet["entities"]:
        for s in tweet["entities"]["symbols"]:
            l_index, r_index = s["indices"][0], s["indices"][1]
            text_list[l_index:r_index] = [None] * (r_index - l_index)
    if remove_hashtags and "hashtags" in tweet["entities"]: 
        for h in tweet["entities"]["hashtags"]:
            l_index, r_index = h["indices"][0], h["indices"][1]
            text_list[l_index:r_index] = [None] * (r_index - l_index)
    if remove_mentions and "user_mentions" in tweet["entities"]:
        for um in tweet["entities"]["user_mentions"]:
            l_index, r_index = um["indices"][0], um["indices"][1]
            text_list[l_index:r_index] = [None] * (r_index - l_index)
    
    text_list = filter(None, text_list)
    return "".join(text_list)


# MENTION functions
def contains_mention(tweet):
    """Takes a python-native tweet obect (a dict). Returns True if a tweet contains a mention"""
    if "entities" not in tweet:
        return False
    return True if len(tweet["entities"]["user_mentions"]) > 0 else False

def num_mentions(tweet):
    """Returns (int) number of mentions in tweet"""
    if contains_mention(tweet):
        return len(tweet["entities"]["user_mentions"])
    return 0

def get_users_mentioned(tweet):
    """
    Takes a native tweet (dict). Returns list of all mentioned users in tuple form 
    (user id_str, user screen name), or empty list if none.
    """
    if not contains_mention(tweet):
        return []
    users = []
    for m in tweet["entities"]["user_mentions"]:
        users.append((m["id_str"], m["screen_name"]))
    return users


# HASHTAG functions
def contains_hashtag(tweet):
    """Returns true if tweet contains one or more hashtags"""
    if "entities" not in tweet:
        return False
    return True if len(tweet["entities"]["hashtags"]) > 0 else False

def num_hashtags(tweet):
    """Returns number of hashtags in a tweet"""
    if contains_hashtag(tweet):
        return len(tweet["entities"]["hashtags"])
    return 0

def get_hashtags(tweet):
    """Returns all tweet hashtags as a list of strings (WITHOUT the '#' char)"""
    if contains_hashtag(tweet):
        return [h["text"] for h in tweet["entities"]["hashtags"]]
    return []

ht_pattern = r"#\w+"
def get_hashtags_from_text(text):
    """A simple RE-based best-effort capturer of hashtags in given text"""
    return re.findall(ht_pattern, text, flags=re.UNICODE)


# URL and Link functions
def contains_url(tweet):
    """Returns True is tweet has at least one 'urls' entity"""
    if "entities" not in tweet:
        return False
    if "urls" in tweet["entities"] and len(tweet["entities"]["urls"]) > 0:
        return True
    return False

def num_urls(tweet):
    """Returns number of URLs in tweet - entities urls field"""
    if contains_url(tweet):
        return len(tweet["entities"]["urls"])
    return 0

def get_urls(tweet):
    """Returns a list of the URLs in tweet (will return multiples if multiples exist in tweet)"""
    if contains_url(tweet):
        return [u["expanded_url"] for u in tweet["entities"]["urls"]]
    else:
        return []

def contains_link(tweet):
    """Returns true if tweet contains link (URL or Media). Checks entities"""
    if "entities" not in tweet:
        return False
    if "urls" in tweet["entities"]:
        if len(tweet["entities"]["urls"]) > 0:
            return True
    if "media" in tweet["entities"]:
        if len(tweet["entities"]["media"]) > 0:
            return True
    return False

def num_links(tweet):
    """Returns the number of links in a tweet (URLs and Media). Checks entities"""
    if not contains_link(tweet):
        return 0
    if "media" not in tweet["entities"]:
        return len(tweet["entities"]["urls"])
    if "urls" not in tweet["entities"]:
        return len(tweet["entities"]["media"])
    return len(tweet["entities"]["urls"]) + len(tweet["entities"]["media"])

def get_links(tweet):
    """Return all link addresses in the tweet"""
    links = []
    if contains_url(tweet):
        links += [u["expanded_url"] for u in tweet["entities"]["urls"]]
    if contains_media(tweet):
        links += [m["expanded_url"] for m in tweet["entities"]["media"]]
    return links

# MEDIA (and image) functions
def contains_media(tweet):
    """Returns True if tweet entities has at least one media entry"""
    if "entities" not in tweet:
        return False
    if "media" in tweet["entities"] and len(tweet["entities"]["media"]) > 0:
        return True
    return False

def num_media(tweet):
    """Returns number of media entity elements in tweet"""
    if contains_media(tweet):
        return len(tweet["entities"]["media"])
    return 0

def contains_image(tweet):
    """Takes a python-native tweet (dict), returns True if tweet contains an image"""
    if "entities" not in tweet:
        return False
    elif "media" not in tweet["entities"]:
        return False
    for m in tweet["entities"]["media"]:
        if m["type"] == "photo":
            return True
    return False

def get_image_urls(tweet):
    """Returns a list of the media urls for each media entity (image) in tweet"""
    urls = []
    if not contains_image(tweet):
        return urls
    for m in tweet["entities"]["media"]:
        urls.append(m["media_url"])
    return urls
