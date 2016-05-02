from collections import OrderedDict

class LimitedSizeDict(OrderedDict):
    """
    Copied from http://stackoverflow.com/questions/2437617/limiting-the-size-of-a-python-dictionary
    """
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("size_limit", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    # May also need to implement other methods, like "update"?

    def _check_size_limit(self):
        if self.size_limit is not None:
          while len(self) > self.size_limit:
            self.popitem(last=False)
