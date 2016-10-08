# -*- coding: utf-8 -*-

import sys
import os
import pickle
import json

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
import queries
from LexAnalyser import LexAnalyser
from PicklePersist import PicklePersist
from Retrievers import VectorRetriever
from Postings import SequentialPostings

def getParameters():
	# Obtengo Queries
	queriesFile = False
	try:
		if os.path.isfile(sys.argv[1]):
			queriesFile = sys.argv[1]
	except IndexError:
		queriesFile = False
	return queriesFile

def getRetrievalRankFromMenu():
	s = []
	s.append("\n")
	s.append("Choose a RANK for the retrieval:\n")
	s.append("1 - Cosine Similarity\n")
	s.append("2 - Scalar Product\n")
	s.append("3 - Dice\n")
	s.append("4 - Jaccard\n")
	s.append("-1 - Salir\n")
	s.append("OTRO - Cosine Similarity\n")
	s.append("\nEnter option: ")
	for line in s:
		print line,

	op = raw_input()
	if op == "-1": sys.exit()
	if op == "1": return VectorRetriever.RANK_COSINE_SIMILARITY
	elif op == "2": return VectorRetriever.RANK_SCALAR_PRODUCT
	elif op == "3": return VectorRetriever.RANK_DICE
	elif op == "4": return VectorRetriever.RANK_JACCARD
	else: return VectorRetriever.RANK_COSINE_SIMILARITY
		
def main():
	# Path en donde se encuentra la data indexada
	INDEX_DIR = "index_data/"
	
	# Chequeo que exista directorio
	if not os.path.exists(INDEX_DIR):
		print "ERROR: Para ejecutar este programa debe antes indexar una coleccion"
		sys.exit()

	# Cargo configuracion del index
	CONFIG_FILE= "config.json"
	config = json.load(open(INDEX_DIR + CONFIG_FILE))
	
	# Cargo index
	pp = PicklePersist()
	print "Cargando vocabulario"
	vocabulary = pp.load(INDEX_DIR+"vocabulary")
	print "Cargando documentos"
	documents = pp.load(INDEX_DIR+"documents")
	print "Cargando postings"
	seqFreqPostings = SequentialPostings(INDEX_DIR+"seq_freq_posting.txt")

	rank = getRetrievalRankFromMenu()
	docsNorm = {}
	if rank != VectorRetriever.RANK_SCALAR_PRODUCT:
		print "Cargando norma de documentos"
		docsNorm =  pp.load(INDEX_DIR+"documentsNorm")

	print "Cargando Retriever"
	vr = VectorRetriever(vocabulary, seqFreqPostings, 
		documents.content, rank=rank, documentsNorm=docsNorm)
	
	# Configuro al query manager
	la = LexAnalyser(config)
	qm = queries.QueriesManager()
	qm.setLexAnalyser(la)

	# Solicito queries
	queriesFile = getParameters()
	if queriesFile:
		qm.setQueriesFromTrecFile(queriesFile)
	else:
		qm.setQueriesFromConsole()

	if qm.queries:
		rank = vr.getRank(qm.queries)
		for q in rank: print "Query %d: %d documentos recuperados" % (q,len(rank[q]))
		vr.printRankingFile(rank,"ranking")

if __name__ == "__main__":
	main()