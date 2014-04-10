from itertools import izip_longest, islice
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
