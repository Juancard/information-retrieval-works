# -*- coding: utf-8 -*-

############## READ_DUMP.py ##################
# Script que lee archivo dump_10k.txt

###############################################

import sys
import os
import codecs
import collections
import time

sys.path.insert(0, os.path.abspath("../../modulos"))
from PicklePersist import PicklePersist
from Postings import BinaryPostings, DictionaryPostings

def getParameters():
	out = []
	try:
		out.append(sys.argv[1])
	except OSError, e:
		print e
		sys.exit()
	except IndexError:
		print """Uso:
	{0} /path/a/corpus
Ejemplo:
	{0} ../corpus/dump10k.txt""".format(sys.argv[0])
		sys.exit()

	return out

def main():
	corpusTxt = getParameters()[0]
	vocabulary = collections.OrderedDict()
	postings = DictionaryPostings({})
	start = time.time()
	with codecs.open(corpusTxt, mode='rt', encoding='utf-8') as f:
		termId = 1
		for line in f:
			term, df, docs = line.rstrip().split(":")
			vocabulary[term] = {
				"id": termId,
				"df": df
			}
			for docId in docs.split(","):
				try: postings.addPosting(termId, int(docId), 1)
				except ValueError: pass
			print "Cargando: ",term
			termId += 1
	
	print "time:",time.time() - start
	postings.sortByKey()

	INDEX_DIR = "index/"
	if not os.path.exists(INDEX_DIR):
	    os.makedirs(INDEX_DIR)
	sp = BinaryPostings.create(postings.getAll(), 
		path=INDEX_DIR, title="binary_postings.dat", dgaps=True)
	#print len(sp.getAll()[1])
	#print sp.createSkipLists()

	#pp = PicklePersist()
	#print "Vocabulario guardado en: %s" % pp.save(vocabulary, INDEX_DIR + "vocabulary")
	#print "Postings guardadas en: %s" % pp.save(postings, INDEX_DIR + "postings")


if __name__ == "__main__":
	main()
