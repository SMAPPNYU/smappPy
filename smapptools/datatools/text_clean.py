"""
Functions and data for cleaning text and tweet data 
(Helpful for LIWC - Linguistic Inquiry Word Count - software)

For unicode => ASCII, consider:

a = <Unicode u"" string with aaa then crazy unicode characters>
>  
a.encode('ascii','ignore')
> 'aaa'
a.encode('ascii','replace')
> 'aaa???????'

@auth dpb
@date 2/11/2014
"""

import re

punctuation_trans = {
    ".": " ",
    ",": " ",
    ";": " ",
    ":": " ",
    "\"": "",
    "!": "",
    "?": "",
    "(": " ",
    ")": " ",
    "[": " ",
    "]": " ",
    "=": " ",
    "/": " ",
    #"#": " ",
    #"@": " ",
}

csvsafe_trans = {
    ",": "[c]",
}

whitespace_trans = {
    "\n": " ",
    "\t": " ",
}

shorthand_trans = {
    "&amp": "and",
    "w/": "with",
    "w/o": "without",
    "b/c": "because",
    "b/t": "between",
    " b4 ": " before ",
    " 2day": " today",
}

number_trans = {
    "1": " one ",
    "2": " two ",
    "3": " three ",
    "4": " four ",
    "5": " five ",
    "6": " six ",
    "7": " seven ",
    "8": " eight ",
    "9": " nine ",
    "0": " zero ",
}

ordinal_trans = {
    "1st": "first",
    "2nd": "second",
    "3rd": "third",
    "4th": "fourth",
    "5th": "fifth",
    "6th": "sixth",
    "7th": "seventh",
    "8th": "eighth",
    "9th": "ninth",
    "10th": "tenth",
    "11th": "eleventh",
    "12th": "twelfth",
}

acronym_trans = [
    (re.compile(r"^US\s|\sUS\s|\sUS$"), " United States "),
    (re.compile(r"^EU\s|\sEU\s|\sEU$"), " European Union "),
]

unicode_trans = {
    u"\u2018": "'",        # left single-quote
    u"\u2019": "'",        # right single-quote
    u"\u201A": ",",        # weird low single-quote/comma
    u"\u201B": "'",        # another left single-quote

    u"\u0027": "'",        # apostrophe
    u"\u05F3": "'",        # hebrew punct. "geresh"
    u"\uFF07": "'",        # full-width apostrophe

    u"\u201C": '"',        # left double-quote
    u"\u201D": '"',        # right double-quote
    u"\u201F": '"',        # weird left double-quote

    u"\uFF06": "and",      # full ampersand
    u"\u0026": "and",      # normal ampersand
    u"\uFE60": "and",      # small ampersand

    u"\u2026": "...",      # ellipsis
    u"\uFF0D": "-",        # full-width hyphen
    u"\u2010": "-",        # hyphen
    u"\u2011": "-",        # hyphen
    u"\u2012": "-",        # figure-dash
}

contraction_trans = { 
    "ain't": "am not",          # are not; is not; has not; have not
    "aren't": "are not",        # am not
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "gonna": "going to",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    #"he'd": "he had / he would",
    "he'd've": "he would have",
    "he'll": "he will",         # he shall
    "he'll've": "he will have", # he shall have
    #"he's": "he has / he is",
    "here's": "here is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    #"how's": "how has / how is / how does",
    #"i'd": "i had / i would",
    "i'd've": "i would have",
    "i'll": "i will",           # i shall
    "i'll've": "i will have",   # i shall have
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",         # it had
    "it'd've": "it would have",
    "it'll": "it will",         # it shall
    "it'll've": "it will have", # it shall have
    #"it's": "it has / it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have", 
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    #"she'd": "she had / she would",
    "she'd've": "she would have",
    "she'll": "she will",           # she shall
    "she'll've": "she will have",   # she shall have
    #"she's": "she has / she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    #"so's": "so as / so is",
    #"that'd": "that would / that had",
    "that'd've": "that would have",
    #"that's": "that has / that is",
    #"there'd": "there had / there would",
    "there'd've": "there would have",
    #"there's": "there has / there is",
    #"they'd": "they had / they would",
    "they'd've": "they would have",
    "they'll": "they will",         # they shall
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    #"we'd": "we had / we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    #"what'll": "what shall / what will",
    #"what'll've": "what shall have / what will have",
    "what're": "what are",
    #"what's": "what has / what is",
    "what've": "what have",
    #"when's": "when has / when is",
    "when've": "when have",
    "where'd": "where did",
    #"where's": "where has / where is",
    "where've": "where have",
    #"who'll": "who shall / who will",
    #"who'll've": "who shall have / who will have",
    #"who's": "who has / who is",
    "who've": "who have",
    #"why's": "why has / why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    #"you'd": "you had / you would",
    "you'd've": "you would have",
    "you'll": "you will",           # you shall
    "you'll've": "you will have",   # you shall have
    "you're": "you are",
    "you've": "you have"
}

def remove_short_words(text, length=3):
    """Removes all words with length < 'length' param"""
    text = [w for w in text.split() if len(w) >= length]
    return " ".join(text)

def remove_link_text(text):
    """Attempts to match and remove hyperlink text"""
    text = re.sub(r"\S*https?://\S*", "", text)
    return text

def http_cleaner(text):
    """Removes mysteriously hanging 'http' instances"""
    text = re.sub(r"^http ", " ", text)
    text = re.sub(r" http ", " ", text)
    text = re.sub(r" http$", " ", text)
    return text

def translate_punctuation(text):
    """Translates some punctuation (not apostrophes) from text. Returns cleaned string"""
    for p in punctuation_trans:
        text = text.replace(p, punctuation_trans[p])
    return text

def remove_all_punctuation(text, keep_hashtags=False, keep_mentions=False):
    """
    Does a strict remove of anything that is not a character in the Unicode character
    properties database, any whitespace char, or optionally a hashtag or mention symbol. 
    Works now with flags=re.U (ie, Unicode) on any non-word char for most languages.
    """
    if keep_mentions and keep_hashtags:
        return re.sub(r"[^\w\s@#]", "", text, flags=re.U)
    elif keep_mentions:
        return re.sub(r"[^\w\s@]", "", text, flags=re.U)
    elif keep_hashtags:
        return re.sub(r"[^\w\s#]", "", text, flags=re.U)
    else:
        return re.sub(r"[^\w\s]", "", text, flags=re.U)

def basic_tokenize(text, lower=True, keep_hashtags=True, keep_mentions=True):
    """
    Basic space-and-punctuation-based tokenization of a string. Removes all non-word
    characters (can keep hashtag and mention characters optionally), returns list of
    resulting space-separated tokens. Optionally lower-cases (default true)
    """
    if lower:
        return remove_all_punctuation(text.lower(),
                                      keep_hashtags=keep_hashtags,
                                      keep_mentions=keep_mentions).split()
    else:
        return remove_all_punctuation(text,
                                      keep_hashtags=keep_hashtags,
                                      keep_mentions=keep_mentions).split()

def get_cleaned_tokens(text, lower=True, keep_hashtags=True, keep_mentions=True, rts=False,
    mts=False, https=False, stopwords=[]):
    """
    Tokenization function specially for cleaning tweet tokens. 
    All parameters represent "keep" parameters:
        lower, keep_hashtags, and keep_mentions are passed to 'basic_tokenize()'
        rts: keep token 'rt' if true, else discard
        mts: keep token 'mt' if true, else discard
        https: keep any token containing 'http' if true, else discard
    """
    tokens = basic_tokenize(text, lower, keep_hashtags, keep_mentions)
    if not rts:
        tokens = [t for t in tokens if t != "rt"]
    if not mts:
        tokens = [t for t in tokens if t != "mt"]
    if not https:
        tokens = [t for t in tokens if not re.search(r"http", t)]
    if stopwords:
        tokens = [t for t in tokens if t not in stopwords]
    return tokens

def remove_RT_MT(text):
    """Removes all hanging instances of 'RT' and 'MT'. NOTE: Expects lower case"""
    text = re.sub(r" rt ", " ", text)
    text = re.sub(r"^rt ", " ", text)
    text = re.sub(r" rt$", " ", text)

    text = re.sub(r" mt ", " ", text)
    text = re.sub(r"^mt ", " ", text)
    text = re.sub(r" mt$", " ", text)
    return text

def clean_whitespace(text):
    """Alternate method of cleaning whitespace"""
    return " ".join(text.split())

def translate_whitespace(text):
    """Replaces any non-single-space whitespace chars (tabs, newlines..). Returns cleaned string"""
    for w in whitespace_trans:
        text = text.replace(w, whitespace_trans[w])
    return text

def csv_safe(text):
    """Makes text CSV-safe (no commas, tabs, newlines, etc). Returns cleaned string"""
    text = clean_whitespace(text)
    for c in csvsafe_trans:
        text = text.replace(c, csvsafe_trans[c])
    return text

def translate_shorthand(text):
    """Translate common shorthand terms into long form. Returns translated string"""
    for s in shorthand_trans:
        text = text.replace(s, shorthand_trans[s])
    return text

def translate_numbers_simple(text):
    """Naive translation of digit characters to corresponding number words. No scaling."""
    for key, rep in number_trans.items():
        text = text.replace(key, rep)
    return text

def translate_ordinals(text):
    """Translate ordinal digit strings up two twelve(fth)"""
    for key, rep in ordinal_trans.items():
        text = re.sub(" {0}".format(key), " {0}".format(rep), text)
        text = re.sub("^{0} ".format(key), "{0} ".format(rep), text)
        text = re.sub(" {0}$".format(key), " {0}".format(rep), text)
    return text

def translate_acronyms(text):
    """Translate common acronyms. WARNING: watch out for words (use spaces). Returns translated string"""
    # acronym_trans is a (re, replacement) tuple
    for a in acronym_trans:
        text = a[0].sub(a[1], text)
    return text

def translate_unicode(text):
    """Translate some unicode characters into better equivalents. Returns translated string"""
    for u in unicode_trans:
        text = text.replace(u, unicode_trans[u])
    return text

def translate_contractions(text):
    """Translates contractions with expanded forms. Returns translated string"""
    for c in contraction_trans:
        text = text.replace(c, contraction_trans[c])
    return text

def remove_stopwords(text, stopwords):
    """
    Standard way to remove stopwords from text. Text is a string. Stopwords is
    a list of strings to remove. Returns cleaned string.
    """
    text = " " + text + " "
    for w in stopwords:
        text = text.replace(u" {0} ".format(w.decode("utf8")), u" ")
    return text.strip()

def remove_digit_words(text):
    """
    Remove all space-separated substrings of only digits. Return cleaned string.
    """
    return " ".join([w for w in text.split() if not w.isdigit()])

def remove_user_mentions(text):
    """
    Removes @mentions from tweets so that "hello @shlomo how are you?" becomes "hello how are you?."
    """
    text = re.sub(r"\S*@\w+\S*", "", text)
    return text
