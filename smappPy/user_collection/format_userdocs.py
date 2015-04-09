"""
Quick script to repair/format userdocs in a given collection

@auth dpb
@date 12/04/2014
"""

import argparse
from pymongo import MongoClient
from smappPy.user_collection.userdocs import format_userdoc_collection

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", default="smapp.politics.fas.nyu.edu",
    help="Database server host [smapp.politics.fas.nyu.edu]")
parser.add_argument("-p", "--port", type=int, default=27011,
    help="Database server port [27011]")
parser.add_argument("-u", "--user", dest="user", default="smapp_readWrite",
    help="Database username [smapp_readWrite]")
parser.add_argument("-w", "--password", default=None,
    help="Database password [None]")
parser.add_argument("-d", "--database", required=True,
    help="Database to store data in")
parser.add_argument("-c", "--collection", required=True,
    help="Collection to store user data in")
parser.add_argument("-ks", "--keep_status", action="store_true", default=False,
    help="Flag to keep user 'status' field in userdocs")
args = parser.parse_args()

client = MongoClient(args.server, args.port)
database = client[args.database]
database.authenticate(args.user, args.password)
collection = database[args.collection]

format_userdoc_collection(collection, delete_status=not args.keep_status)
