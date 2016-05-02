"""
Contains functions for stopwords and stopwords lists not found in NLTK

@auth dpb
"""

import codecs

def stopwords_from_file(infile, delimiter="\n"):
    """
    Parses stopwords from file, returns list of stopwords.
    Delimiter indicates stopword separator.
    """
    with codecs.open(infile, encoding="utf8") as handle:
        fstr = handle.read()
        words = fstr.strip().split(delimiter)
    return [w.strip() for w in words if w.strip() != ""]