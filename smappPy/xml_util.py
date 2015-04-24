"""
Utility functions relating to dealing with xml files.

@jonathanronen 2015/4
"""

mpa = dict.fromkeys(range(20))
def clear_unicode_control_chars(text):
    return text.translate(mpa)