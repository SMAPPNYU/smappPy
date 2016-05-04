"""
Writes an outfile of top topic words
"""

import argparse

from gensim import corpora, models
from smappPy.topics.utilities import get_topic_wpl_string

# Commandline
parser = argparse.ArgumentParser()
parser.add_argument("-mf", "--modelfile", required=True,
    help="File containing serialized gensim LDA model")
parser.add_argument("-o", "--outfile", required=True,
    help="File to write topic text to")
parser.add_argument("-n", "--topn", type=int, default=30,
    help="Number of top words to write per topic")
args = parser.parse_args()

# Load model
model = models.ldamodel.LdaModel.load(args.modelfile)

with open(args.outfile, "w") as outhandle:
    for t in range(model.num_topics):
        outhandle.write(get_topic_wpl_string(model, t, top_n=args.topn) + "\n")

print "Complete. Outfile: {0}".format(args.outfile)
