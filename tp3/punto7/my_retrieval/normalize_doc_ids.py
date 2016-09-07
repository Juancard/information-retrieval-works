# -*- coding: utf-8 -*-
import sys
import os
import unicodedata
import re

script_dir = os.path.dirname(__file__) 
pathTerrier = os.path.join(script_dir, "../terrier_retrieval/collection.spec")
pathMyRetrieval = os.path.join(script_dir, "id_to_doc_mapping.txt")
pathMyRank = os.path.join(script_dir, "ranking.res")

with open(pathTerrier) as f:
	terrierDocs = {}
	docId = 1
	for line in f:
		if line.startswith("/"):
			a = line.rsplit('\n')[0].split("/")
			terrierDocs[docId] = a[len(a)-1]
			docId += 1

with open(pathMyRetrieval) as f:
	myDocs = {}
	for line in f:
		a = line.rsplit('\n')[0].split(" ")
		myDocs[int(a[0])] = a[1]

with open("normalized_ranking.res", "w") as newFile:
	docIdPosition = 2
	with open(pathMyRank) as oldFile:
		for line in oldFile:
			a = line.split(" ")
			docId = int(a[docIdPosition])
			if docId in myDocs:
				names = [d for d in terrierDocs if terrierDocs[d] == myDocs[docId]]
				if len(names) > 1:
					print "WARNING: There are %d documents for doc name %s" % (len(names), myDocs[docId])
				elif len(names) == 0:
					print "No Id for doc name %s" % myDocs[docId]
				else:
					a[docIdPosition] = str(names[0])
			newFile.write(" ".join(a))

