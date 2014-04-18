"""
Functions to clean documents and output updated doc files
"""

from smappPy.text_clean import *
from collections import defaultdict
from tempfile import NamedTemporaryFile


def clean_docs(doc_iterator, out_handle, stopwords, keep_hashtags, 
        keep_mentions, occurrence_threshold=3):
    """
    Given an iterator over documents, cleans each document and then writes to
    given out_handle. 
    Will create a named Python tempfile in order to avoid keeping all semi-
    cleaned docs (intermediary stage) in memory.
    @Params:
      stopwords - list of stopwords to remove from documents
      occurrence_threshold  - number of times a word must appear in the corpus
                              to not be removed from all documents.

    Text cleaning via smappPy and nltk (stopwords):
      1 - remove trailing newlines and lowercase
      2 - translate common twitter shorthand (EN)
      3 - translate troublesome unicode chars into ASII
      4 - translate contractions into long form (EN)
      5 - remove hanging RT and MT strings
      6 - remove ALL punctuation (except mention and hastag symbols)
      7 - normalize whitespace
      8 - remove all stopwords
      9 - apply 'occurrence_threshold'
    """
    print "Building up word counts and cleaning document text"
    word_counts = defaultdict(int)
    tmp_handle = NamedTemporaryFile()
    doc_count = 1
    for doc in doc_iterator:
        print "Processing doc {0}".format(doc_count)
        doc_count += 1

        doc = doc.strip().lower()
        # print ".. Trans shorthand"
        doc = translate_shorthand(doc)
        # print ".. Trans unicode"
        doc = translate_unicode(doc)
        # print ".. Trans contractions"
        doc = translate_contractions(doc)
        # print ".. Remove RT/MT"
        doc = remove_RT_MT(doc)
        # print ".. Remove Link text"
        doc = remove_link_text(doc)     # MUST BEFORE PUNCTUATION
        # print ".. Remove punctuation"
        doc = remove_punctuation(doc)
        # print ".. Remove hanging 'http's"
        doc = http_cleaner(doc)
        # print ".. Remove short words"
        doc = remove_short_words(doc)
        # print ".. Remove stopwords"
        doc = clean_whitespace(doc)
        doc = " " + doc + " " 
        for w in stopwords:
            doc = doc.replace(u" {0} ".format(w.decode("utf8")), u" ")
        doc = doc.strip()


        for w in doc.split():
            word_counts[w] += 1

        # Write temporary document to tmp (re-stream, avoid holding all in mem)
        tmp_handle.write("{0}\n".format(doc.encode("utf8")))

    print "{0} tokens".format(len(word_counts))
    print "Thresholding based on word occurrence: {0}".format(occurrence_threshold)

    tmp_handle.seek(0)
    for doc in tmp_handle:
        doc = doc.strip().decode("utf8")
        doc = [w for w in doc.split() if word_counts[w] >= occurrence_threshold]
        doc = " ".join(doc)
        out_handle.write("{0}\n".format(doc.encode("utf8")))
    tmp_handle.close()
