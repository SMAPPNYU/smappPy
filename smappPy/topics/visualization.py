"""
Topic visualization functions

Relies on GENSIM objects

@auth dpb
@date 3/25/2014
"""

import matplotlib.pyplot as plt
from collections import defaultdict

def topic_sum_barchart(corpus, model, show=False, outfile=None, bar_width=0.5, trim_threshold=0.0, normed=True):
    """
    Sums the probabilities of each topic across all documents in a corpus. Creates barcharts of sums.
    show=True runs matplotlib show.
    Specify an outfile value to save to disk as pdf
    trim_threshold allows for not displaying topics with a sum probability across all documents
    of < given value (default 0.0, ie display all topics)
    normed=True indicates that the sum values should be normalized (averaged) over the number of docs in
    the corpus
    """
    topic_p_dict = defaultdict(float)
    for doc in corpus:
        for doc_topic in model[doc]:
            topic_p_dict[doc_topic[0]] += doc_topic[1]

    topic_ids = []
    topic_counts = []

    for (tid, sum_p) in topic_p_dict.items():
        if sum_p >= trim_threshold:
            topic_ids.append(tid)
            topic_counts.append(sum_p)

    if normed:
        num_docs = len(corpus)
        plt.bar(range(len(topic_ids)), [sp / num_docs for sp in topic_counts], width=bar_width, linewidth=0, color="blue", alpha=0.75)
        plt.ylabel("Normalized P over all documents (p >= {0})".format(trim_threshold))
        plt.title("Normalized Topic Probability")
    else:
        plt.bar(range(len(topic_ids)), topic_counts, width=bar_width, linewidth=0, color="blue", alpha=0.75)
        plt.ylabel("Sum P over all documents (if >= {0})".format(trim_threshold))
        plt.title("Sum Topic Probability")
    
    plt.xlabel("Topics")
    plt.tick_params(axis="x", which="both", bottom="off", top="off", labelbottom="on")
    plt.xticks(range(len(topic_ids)), topic_ids)
    plt.tight_layout()

    if outfile != None:
        print "(Saving figure to file '{0}'')".format(outfile)
        plt.savefig(outfile, format="pdf")
    if show:
        print "(Showing plot via matplotlib)"
        plt.show()

    plt.clf()
    plt.close()


def topic_occurrence_barchart(corpus, model, topic_threshold=0.2, show=False, outfile=None, bar_width=0.5, trim=True):
    """
    Creates barchart of occurences of each topic in each document with a P > topic_threshold.
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

    plt.bar(range(len(topic_ids)), topic_counts, width=bar_width, linewidth=0, color="red", alpha=0.75)    
    plt.xlabel("Topics")
    plt.ylabel("Occurences P >= {0}".format(topic_threshold))
    plt.title("Topic Occurrence")
    plt.tick_params(axis="x", which="both", bottom="off", top="off", labelbottom="on")
    plt.xticks(range(len(topic_ids)), topic_ids)
    plt.tight_layout()

    if outfile != None:
        print "(Saving figure to file '{0}'')".format(outfile)
        plt.savefig(outfile, format="pdf")
    if show:
        print "(Showing plot via matplotlib)"
        plt.show()

    plt.clf()
    plt.close()
