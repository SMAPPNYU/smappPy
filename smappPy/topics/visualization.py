"""
Topic visualization functions

Relies on GENSIM objects

@auth dpb
@date 3/25/2014
"""

import matplotlib.pyplot as plt

from collections import defaultdict

def topic_barchart(corpus, model, topic_threshold=0.2, show=False, outfile=None, bar_width=0.2, trim=True):
    """Creates an additive histogram of topic presence over documents in given corpus.
    Basically, counts occurences of each topic in each document with a P > topic_threshold.
    show=True runs matplotlib show.
    Specify an outfile value to save to disk as pdf
    If trim=True, remove all 0-count values and then display (maintain indexes)
    """
    topic_count_dict = defaultdict(int)
    for doc in corpus:
        for doc_topic in model[doc]:
            if doc_topic[1] >= topic_threshold:
                topic_count_dict[doc_topic[0]] += 1

    topic_ids = []
    topic_counts = []
    if trim:
        for (tid, count) in topic_count_dict.items():
            if count > 0:
                topic_ids.append(tid)
                topic_counts.append(count)
    else:
        for (tid, count) in topic_count_dict.items():
            topic_ids.append(tid)
            topic_counts.append(count)

    plt.bar(range(len(topic_ids)), topic_counts, width=bar_width, linewidth=0, color="#9b59b6")
    plt.xlabel("Topics")
    plt.ylabel("Occurences P >= {0}".format(topic_threshold))
    plt.title("Topic Occurrence")
    plt.xticks(range(len(topic_ids)), topic_ids, rotation=55)

    if outfile != None:
        print "(Saving figure to file '{0}'')".format(outfile)
        plt.savefig(outfile, format="pdf")
    if show:
        print "(Showing plot via matplotlib)"
        plt.show()

