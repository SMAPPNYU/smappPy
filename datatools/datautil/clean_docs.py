"""
Functions to clean documents and output updated doc files
"""

from smappPy.text_clean import *
from collections import defaultdict
from tempfile import NamedTemporaryFile


def clean_docs(doc_iterator, 
               out_handle, 
               clean_functions=[translate_shorthand, 
                                translate_unicode, 
                                translate_contractions,
                                remove_RT_MT,
                                remove_link_text,
                                remove_all_punctuation,
                                http_cleaner,
                                remove_short_words,
                                clean_whitespace],
               stopwords=[], 
               occurrence_threshold=3,
               print_progress_every=1):
    """
    Given an iterator over documents, cleans each document and then writes to
    given out_handle. 
    Will create a named Python tempfile in order to avoid keeping all semi-
    cleaned docs (intermediary stage) in memory.
    @Params:
      stopwords - list of stopwords to remove from documents
      occurrence_threshold  - number of times a word must appear in the corpus
                              to not be removed from all documents.

    Text cleaning via chain of functions (see smappPy.text_clean for examples)
    """
    print "Building up word counts and cleaning document text"
    word_counts = defaultdict(int)
    tmp_handle = NamedTemporaryFile()
    doc_count = 1
    for doc in doc_iterator:
        if doc_count % print_progress_every == 0:
            print "Processing doc {0}".format(doc_count)
        doc_count += 1

        doc = doc.strip().lower()
        for cf in clean_functions:
            doc = cf(doc)
        
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
