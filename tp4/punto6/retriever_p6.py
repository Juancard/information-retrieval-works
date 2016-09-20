# -*- coding: utf-8 -*-
###################################################
#6) Modifique su programa anterior para que realice 
#	indexación posicional y soporte búsquedas
#   booleanas por frases.
###################################################

import sys
import os
import pickle
import json

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
from queries import QueriesManager
from LexAnalyser import LexAnalyser
from PicklePersist import PicklePersist
from Retrievers import BooleanRetriever
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

def printRank(docsRank, documents):
	for q in docsRank:
		print "-" * 50
		print "Query:", q
		print "-" * 50
		if not docsRank[q]:
			print "Sin resultados"
		else:
			rank = 1
			for doc in docsRank[q]:
				print "Rank %d: %s" % (rank, documents.content[doc])
				rank += 1

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
	print "Cargando postings con frecuencias"
	seqFreqPostings = SequentialPostings(INDEX_DIR+"seq_freq_posting.txt")
	print "Cargando postings posicionales"
	seqPositionalPostings = SequentialPostings(INDEX_DIR+"seq_position_posting.txt")

	# Configuro al query manager
	la = LexAnalyser(config)
	qm = QueriesManager(phraseOperator=True)
	qm.setLexAnalyser(la)

	# Solicito queries
	queriesFile = getParameters()
	if queriesFile:
		qm.setQueriesFromTrecFile(queriesFile)
	else:
		qm.setQueriesFromConsole()

	# Realizo recuperacion
	if qm.queries:
		br = BooleanRetriever(vocabulary, seqPositionalPostings, documents.content)
		docsRank = br.retrieve(qm.queries)
		# Muestro resultados
		printRank(docsRank, documents)

if __name__ == "__main__":
	main()