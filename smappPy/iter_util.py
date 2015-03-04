from itertools import izip_longest, islice

def get_ngrams(input_list, n):
    """
    Return all n-grams from list. Cred: 
    http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
    """
    return zip(*[input_list[i:] for i in range(n)])

def grouper(n, iterable, fillvalue=None, pad=True):
    """
    Split iterable into chunks of data:
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    grouper(3, 'ABCDEFG', 'x', pad=False) --> ABC DEF G
    """
    if pad:
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)
    else:
        return grouper_no_fill(n, iterable)

def grouper_no_fill(n, iterable):
    "grouper_no_fill(3, 'ABCDEFG') --> ABC DEF G"
    it = iter(iterable)
    while True:
       chunk = tuple(islice(it, n))
       if not chunk:
           return
       yield chunk
