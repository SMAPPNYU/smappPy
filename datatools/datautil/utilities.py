"""
Utility functions for topic models

Relies heavily on Gensim object (http://radimrehurek.com/gensim/apiref.html)

@auth dpb
@date 3/25/2014
"""

def print_topics(model, num_topics=-1, top_n=5, ordered=True):
    """Prints formatted topic strings"""
    for tstr in get_topic_strings(model, num_topics, top_n, ordered):
        print tstr

def print_topics_wpl(model, num_topics=-1, top_n=5, ordered=True):
    """Prints formatted topics, with Topic heading and then word-per-line"""
    for tstr in get_topic_strings(model, num_topics, top_n, ordered, wpl=True):
        print tstr

def print_doc_topics(corpus, model, num_docs=-1, topic_threshold=0.2,  min_topics=2, topic_words=5):
    """Prints a document-topic string for given parameters"""
    for dtstr in get_doc_topic_strings(corpus, 
                                       model, 
                                       num_docs=num_docs, 
                                       topic_threshold=topic_threshold,
                                       min_topics=min_topics,
                                       topic_words=topic_words):
        print dtstr

def get_short_topic_string(model, topic_id, top_n=5):
    """Shorter version of string"""
    topic = model.show_topic(topic_id, topn=top_n)
    tstr = "{"
    for (p,word) in topic:
        tstr += "{0}, ".format(word)
    tstr = tstr.rstrip(", ") + "}"
    return tstr

def get_topic_string(model, topic_id, top_n=5):
    """Get string of topic with Id (index) topic_id"""
    # List of (p,word) tuples
    topic = model.show_topic(topic_id, topn=top_n)
    tstr = "Topic {0}:".format(topic_id)
    for (p,word) in topic:
        tstr += " {0:.3f} {1:<10} |".format(p, word)
    return tstr

def get_topic_wpl_string(model, topic_id, top_n=5):
    """Get string repr of topic with word-per-line"""
    topic = model.show_topic(topic_id, topn=top_n)
    tstr = "Topic {0}:".format(topic_id)
    for p,word in topic:
        tstr += "\n\t{0:.3f} {1}".format(p, word.encode("utf8"))
    return tstr

def get_topic_strings(model, num_topics=-1, top_n=5, ordered=True, wpl=False):
    """Given a model with trained topics, return list of formatted topic strings.
    If num_topics=-1, prints all topics
    If ordered=False, prints random selection of topics (via gensim show_topics)
    If ordered=True, prints topics in order, with associated topic ID
    If wpl=True, get word-per-line topic strings (multiline output per topic)
    """
    tstrings = []
    if num_topics > model.num_topics:
        print "(Warning: model only has {0} topics)".format(model.num_topics)
        num_topics = model.num_topics
    elif num_topics == -1:
        num_topics = model.num_topics
    
    if ordered:
        topics = [model.show_topic(i, topn=top_n) for i in range(num_topics)]
    else:
        topics = model.show_topics(topics=num_topics, topn=top_n, log=False, formatted=False)
    
    for i in range(len(topics)):
        tstr = "Topic {0}: ".format(i) if ordered else "Topic: "
        for wordprob in sorted(topics[i], key=lambda p: p[0], reverse=True):
            if wpl:
                tstr += "\n\t{0:.3f} {1}".format(wordprob[0], wordprob[1])
            else:
                tstr += " {0:.3f} {1:<15} |".format(wordprob[0], wordprob[1])
        tstrings.append(tstr)

    return tstrings

def get_doc_topic_strings(corpus, model, num_docs=-1, topic_threshold=0.2, min_topics=2, topic_words=5):
    """Given a corpus of documents and a model, get strings representing the topics 
    assigned to each document with probability over 'topic_threshold'
    If num_docs is -1, get all document strings
    topic_threshold is a low-threshold for topic probability per document
    min_topics is the minimum number of topics shown per document, overriding the topic_threshold
    Note that if the document is assigned fewer than min_topics, as many as are available will be displayed 
    """
    if num_docs > corpus.num_docs:
        print "(Warning: corpus only contains {0} documents)".format(corpus.num_docs)
        num_docs = corpus.num_docs
    elif num_docs == -1:
        num_docs = corpus.num_docs

    doc_strings = []
    for i in range(num_docs):
        doc_string = "Document {0}:\n".format(i)
        count = 0
        for doc_topic in sorted(model[corpus[i]], key=lambda p: p[1], reverse=True):
            if count < min_topics or doc_topic[1] >= topic_threshold:
                doc_string += "\tTopic {0} ({1:.3f}): ".format(doc_topic[0], doc_topic[1])  
                topic_strings = ["{0} ({1:.3f})".format(t[1], t[0]) for t in model.show_topic(doc_topic[0], topn=topic_words)]
                doc_string += ", ".join(topic_strings)
                doc_string += "\n"
                count += 1
            else:
                break
        doc_strings.append(doc_string)

    return doc_strings