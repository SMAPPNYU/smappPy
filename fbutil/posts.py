"""
Module for getting texts from facebook posts.

@jonathanronen
"""

STANDARD_ENDINGS = [
    'a new photo',
    'created an event',
    'her cover photo',
    'her own link',
    'her own photo',
    'her own status',
    'her own video',
    'his cover photo',
    'his own link',
    'his own photo',
    'his own status',
    'his own video',
    'likes a link',
    'likes a photo',
    'likes a post',
    'likes a status',
    'on a link',
    'on a photo',
    'on a post',
    'shared a link',
    'their own video',
    'their cover photo',
    'their own link',
    'their own photo',
    'their own status',
]
def is_meaningless(post):
    text = get_text(post).strip('.')
    return any(text.endswith(standard_ending) for standard_ending in STANDARD_ENDINGS)

def get_text(post):
    return post.get('message', post.get('story', '')).lower().strip()