"""
Create a simple barchart showing occurrences of topics over a threshold
"""

import argparse

from gensim import corpora, models
from smappPy.topics.visualization import *

parser = argparse.ArgumentParser()
parser.add_argument("-cf", "--corpusfile", required=True,
    help="BOW corpus file (MM format)")
parser.add_argument("-mf", "--modelfile", required=True,
    help="File containing serialized gensim LDA model")
parser.add_argument("--sum_threshold", type=float, default=0.0,
    help="Sum P threshold above which to show a topic's sum P")
parser.add_argument("--occ_threshold", type=float, default=0.2,
    help="Probability threshold above which to count a topic for a document")
parser.add_argument("--sum_outfile", default=None,
    help="Outfile for storing sum barchart (None)")
parser.add_argument("--occ_outfile", default=None,
    help="Outfile for storing occurrence barchart (None)")
parser.add_argument("--show", action="store_true", default=False,
    help="Flag to show figures when generated")
args = parser.parse_args()

# Load corpus and model
c = corpora.mmcorpus.MmCorpus(args.corpusfile)
lda = models.ldamodel.LdaModel.load(args.modelfile)

print "Topic sum barchart"
if args.sum_outfile:
    topic_sum_barchart(c, lda, trim_threshold=args.sum_threshold, show=args.show, outfile=args.sum_outfile)
else:
    topic_sum_barchart(c, lda, trim_threshold=args.sum_threshold, show=args.show)

print "Topic occurrence barchart"
if args.occ_outfile:
    topic_occurrence_barchart(c, lda, topic_threshold=args.occ_threshold, show=args.show, outfile=args.occ_outfile)
else:
    topic_occurrence_barchart(c, lda, topic_threshold=args.occ_threshold, show=args.show)

print "Complete"