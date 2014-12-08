"""
Functions and data for friend/follower network edges, etc.

@auth dpb
@date 12/08/2014
"""

from datetime import datetime
from pymongo import ASCENDING, DESCENDING

def ensure_edge_indexes(collection):
	"""
	Ensures proper indexes for mongo edge collections
	"""
	collection.ensure_index("from", name="from_id", background=True)
	collection.ensure_index("to", name="to_id", background=True)
	collection.ensure_index([("from", ASCENDING),("to", ASCENDING)],
		name="compound_unique", unique=True, drop_dups=True, background=True)


def create_edge_doc(from_id, to_id, timestamp=None):
	"""
	Creates a document representing a network edge. Default timestamp
	is now()
	"""
	return {
		"from": from_id,
		"to": to_id,
		"timestamp": datetime.now()
	}