"""
Basic file utilities
"""

import os
import sys

def overwrite_check(filename):
    """Prompts user for input regarding existing file: overwrite or not (default not)"""
    if os.path.isfile(filename):
        resp = raw_input("Warning: File {0} already exists. Overwrite? y|[n]: ".format(filename))
        if not (resp == "y" or resp == "yes"):
            print "Exiting, please user another file"
            sys.exit(0)