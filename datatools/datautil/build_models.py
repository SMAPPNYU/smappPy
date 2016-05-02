"""
Functions to build topic models given corpus and dict objects

@auth dpb
@date 10/28/2014
"""

from gensim import models

def online_lda(corpus, dictionary, k=25, alpha="symmetric", chunk_size=10000, update_every=1, passes=1):
	"""
	Build the standard online LDA topic model (see gensim:
	http://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation)
	
	Updates model every 'update_every' chunks, does 'passes' full passes over the corpus (updating
	every 'update_every' time each pass), and breaks corpus into 'chunk_size' document chunks.

	EG: chunk_size=100, update_every=1, passes=1: Does one full pass over the corpus, updating the
	model every one chunk, breaking the whole corpus into corpus_size/chunk_size chunks. 

	500 documents => 5 chunks, updates model on every chunk.

	Alpha values can be "symmetric", "asymmetric", and "auto". See: 
	http://radimrehurek.com/gensim/models/ldamodel.html
	"""
	return models.ldamodel.LdaModel(corpus=corpus,
									id2word=dictionary,
									num_topics=k,
									alpha=alpha,
									chunksize=chunk_size,
									update_every=update_every,
									passes=passes)


def batch_lda(corpus, dictionary, k=25, alpha="symmetric", passes=20):
	"""
	Build basic batch LDA topic model (see gensim:
	http://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation)

	Does 'passes' number of passes over the whole corpus, no chunking, and updates the model
	at the end of every full pass.

	Alpha values can be "symmetric", "asymmetric", and "auto". See: 
	http://radimrehurek.com/gensim/models/ldamodel.html
	"""
	return models.ldamodel.LdaModel(corpus=corpus,
								   id2word=dictionary,
								   num_topics=k,
								   alpha=alpha,
								   update_every=0,
								   passes=passes)