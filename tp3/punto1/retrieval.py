# -*- coding: utf-8 -*-

#
# RETRIEVAL.PY
#
# ESTE SCRIPT RECIBE COMO PARAMETROS EL VOCABULARIO, 
# LOS DOCUMENTOS Y LAS QUERIES Y DEVUELVE DOS TXT
# UNO CON LA RECUPERACIÓN REALIZADA EN MODELO BOOLEANO
# Y EL OTRO EN MODELO VECTORIAL. 
#
#

import sys
import os
import re

#-------------------FUNCTIONS------------------

def getVocabulary(path):
	vocabulary = {}
	with open(path) as f:
		next(f)
		for linea in f:
			if linea:
				linea = linea.rstrip().split()
				if len(linea) == 3:
					vocabulary[int(linea[0])] = {
						"idf": float(linea[1]),
						"term": linea[2]
					}
	return vocabulary

# donde formato de archivo es a:
# header1 header2
# xxx 1: (44, 51, 96, 128, 129, 151, 195)
# xxx 2: (3, 10, 25, 35, 37, 44, 46, 51, 58)
def readVectorFile(path):
	out = []
	with open(path) as f:
		next(f)
		pattern = re.compile(r'[a-zA-Z]+\s(\d+)\:\s\(((?:\d+(?:,\s?)?)+)\)')
		for linea in f:
			m = pattern.match(linea)
			if m:
				out.append(m.groups())
	return out

def getVector(path):
	vector = {}
	vectorRead = readVectorFile(path)
	for vectorId, vectorStringValues in vectorRead:
		values = [int(v) for v in vectorStringValues.split(",")]
		vector[int(vectorId)] = {}
		for v in values:
			vector[int(vectorId)][v] = {}
	return vector

def loadWeights(vector, vocabulary):
	for value in vector:
		for t in vector[value]:
			if t in vocabulary:
				vector[value][t] = vocabulary[t]["idf"]
			else:
				vector[value][t] = 0.0
	return vector


def displayRetrievalMenu():
	s = []
	s.append("\n")
	s.append("Choose a retrieval Model:\n")
	s.append("1 - Boolean model\n")
	s.append("2 - Vector space model\n")
	s.append("3 - Both\n")
	s.append("Enter option: ")
	for line in s:
		print line,
	return raw_input()


def booleanRetrieval(queries, documents):
	docsRank = {}
	for qId in queries:
		retrieved = set()
		for term in queries[qId]:
			for docId in documents:
				if term in documents[docId]:
					retrieved.add(docId)
		docsRank[qId] = retrieved
	return docsRank

def dotProduct(vector1, vector2):
	out = 0.0
	for value in vector1:
		if value in vector2:
			out += vector1[value] * vector2[value]
	return out

def sumSquare(vector):
	out = 0.0
	for value in vector:
		out += vector[value] ** 2.0
	return out ** 0.5

def cosineSimilarity(vector1, vector2):
	dp = dotProduct(vector1, vector2)
	normaV1 = sumSquare(vector1)
	normaV2 = sumSquare(vector2)
	return (dp / (normaV1 * normaV2))

def vectorRetrieval(queries, documents):
	docsRank = {}	
	for qId in queries:
		docsRank[qId] = {}
		for docId in documents:
			dp = dotProduct(queries[qId], documents[docId])
			if dp > 0:
				docsRank[qId][docId] = {
					"dotProduct": dp,
					"cosineSimilarity": cosineSimilarity(queries[qId], documents[docId])
				}
	return docsRank

def printBoolean(docsRank):
	with open("booleanModel.txt", "w") as booleanFile:
		s = []
		s.append("query\trank\tdoc\n")
		for qId in docsRank:
			rank = 1
			for docId in docsRank[qId]:
				s.append("%d\t%d\t%d\n" % (qId, rank, docId))
				rank += 1
		booleanFile.write(''.join(s))
		print "File \"booleanModel.txt\" correctly generated"

def printVector(docsRank):
	with open("vectorModel.txt", "w") as booleanFile:
		s = []
		s.append("query\trank\tdoc\tsim\n")
		for qId in docsRank:
			rank = 1
			for docId in sorted(docsRank[qId], key=lambda x: (docsRank[qId][x]['cosineSimilarity']), reverse=True):
				s.append("%d\t%d\t%d\t%f\n" % (qId, rank, docId, docsRank[qId][docId]['cosineSimilarity']))
				rank += 1
		booleanFile.write(''.join(s))
		print "File \"vectorModel.txt\" correctly generated"

# Archivo opcional para ver de cada documento los terminos 
# (id traducido a string corresp.)
def printDocsWithTerms(documentVector):
	with open("docsWithTerms.txt", "w") as f:
		s = []
		s.append("id\tterms")
		for docId in documentVector:
			s.append("\n%d\t" % (docId)) 
			for t in documentVector[docId]:
				s.append("%s " % (vocabulary[t]["term"]))
		f.write(''.join(s))
		print "File \"docsWithTerms.txt\" correctly generated"

# Obtengo parametros que son vocabulary, documentVector y queries
def getParameters():
	#Obtengo parametros
	for i in range(1,4):
		try:
			sys.argv[i]
			if not(os.path.isfile(sys.argv[i])):
				print "Error en parametro %d. Path no válido" % (i) 
				sys.exit()
		except IndexError:
			print "Uso:"
			print "%s /path/to/vocabulary.txt /path/to/documentVector.txt /path/to/queries.txt" % sys.argv[0]
			print "Ejemplo:"
			print "%s " % sys.argv[0],
			print "/home/user/corpus/ejemploRibeiro/vocabulary.txt /home/user/corpus/ejemploRibeiro/documentVector.txt /home/user/corpus/ejemploRibeiro/queries.txt"
			sys.exit()
	return sys.argv[1:4]

def main():

	parameters = getParameters()
	pathVocab = parameters[0]
	pathDoc = parameters[1]
	pathQueries = parameters[2]

	print "Loading vocabulary"
	vocabulary = getVocabulary(pathVocab)

	print "Loading document vector"
	documentVector = loadWeights(getVector(pathDoc), vocabulary)

	print "Loading queries"
	queries = loadWeights(getVector(pathQueries), vocabulary)

	option = displayRetrievalMenu() 
	if option == "1":
		printBoolean(booleanRetrieval(queries, documentVector))
	elif option == "2":
		printVector(vectorRetrieval(queries, documentVector))
	elif option == "3":
		printBoolean(booleanRetrieval(queries, documentVector))
		printVector(vectorRetrieval(queries, documentVector))
	else:
		print "Not a valid option. Terminating program"
		sys.exit()

#--------------------END-FUNCTIONS-------------------

if __name__ == "__main__":
	main()





