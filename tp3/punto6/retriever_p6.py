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

def getParameters():
	# Obtengo Queries
	queriesFile = False
	try:
		if os.path.isfile(sys.argv[1]):
			queriesFile = sys.argv[1]
	except IndexError:
		queriesFile = False
	return queriesFile

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
	postings = pp.load(INDEX_DIR+"postings")
	print "Cargando documentsTerms"
	documentsTerms = pp.load(INDEX_DIR+"documentsTerms")
	print "Cargando Retriever"
	vr = VectorRetriever(vocabulary, postings, documents, documentsTerms)


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
		#vr.setRank(VectorRetriever.RANK_JACCARD)
		rank = vr.getRank(qm.queries)
	
		for q in rank: print "Query %d: %d documentos recuperados" % (q,len(rank[q]))
		vr.printRankingFile(rank,"ranking")

if __name__ == "__main__":
	main()