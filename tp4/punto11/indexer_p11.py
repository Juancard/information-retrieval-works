# -*- coding: utf-8 -*-
import sys
import os
import json
import numpy as np
import collections 

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
from Collection import Collection
from Indexer import Indexer
import IntegerCodes as ic

def getParameters():
	out = []
	try:
		out.append(Collection(sys.argv[1]))
	except OSError, e:
		print e
		sys.exit()
	except IndexError:
		print """Uso:
	{0} /path/a/corpus [/path/to/stop-words.txt]
Ejemplos:
	{0} ../corpus/T12012-gr stopwords.txt
	{0} ../corpus/T12012-gr""".format(sys.argv[0])
		sys.exit()

	# Stopwords
	try:
		stopwords = sys.argv[2]
	except IndexError:
		stopwords = False
	out.append(stopwords)

	return out

def to_unary(n):
	out = ""
	for i in range(0, n):
		out += str(1)
	return out+str(0)

def from_unary(unary):
	out = 0
	for char in unary:
		if char == str(0):
			return out
		else:
			out += 1

def deltaEncode(docs):
	previousValue = docs[0]
	for i in range(1, len(docs)):
		aux = docs[i]
		docs[i] = docs[i] - previousValue
		previousValue = aux
	return docs

def deltaDesencode(docs):
	acum = 0
	for i in range(len(docs)):
		acum += docs[i]
		docs[i] = acum
	return docs

def compress(toCompress):
	compressed = []

	# K: entero a comprimir
	for k in toCompress:

		# KD: cantidad de digitos binarios que escribo
		# Se guarda en unario
		kd = int(np.log2(k))
		kdUnary = to_unary(kd)

		# KR: valor resultante de quitar el primer bit (que siempre es uno si k>0)
		# Se guarda en binario
		kr = k - np.power(2, kd)
		krBinary = ic.dec_to_headless(k)

		compressed += kdUnary + krBinary

	return compressed

def decompress(compressed):
	decompressed = []

	# Se empieza leyendo valor en unario
	isUnary = True
	# Y seteo variable kd a nulo 
	kd = None

	# Se inicializa bits de kd unario
	kdUnary = ""

	# Se inicializa valor k en binario 
	# se pone un uno ya que lo comprimido es un kr (cadena de bits sin primer bit uno)
	kBinary = str(1)


	# Se lee cada bit comprimido
	for bit in compressed:

		# bit es de una palabra en unario? 
		if isUnary:
			kdUnary += bit
			# Si el bit leido es 0, se termina de leer unario
			if bit == str(0):
				kdUnary += bit
				kd = from_unary(kdUnary)
				kdUnary = ""
				isUnary = False

		# Si no es unario, es binario
		else:
			kBinary += bit
			kd -= 1

		# kd igual a cero significa que se termina de leer bits de palabra binaria
		if kd is not None and kd == 0:
			k = ic.bin_to_dec(list(kBinary), len(kBinary))
			decompressed.append(k)
			kBinary = str(1)
			isUnary = True
			kd = None

	return decompressed

def main():
	# Obtengo parametros
	p = getParameters()
	collection = p[0]
	stopwords = p[1]

	# data para el analizador lexico
	indexConfig = {
		"stopwords": stopwords,
		"stem": "spanish",
		"term_min_size": 3,
		"term_max_size": 23
	}
	
	# Indexo
	indexer = Indexer(collection)
	indexer.index(indexConfig)

	postings = indexer.postings.getAll()
	postingsCompressed = {}
	for p in postings:
		# Obtengo listas a comprimir
		docs = deltaEncode(postings[p].keys())
		freqs = [int(k) for k in postings[p].values()]
		
		# Comprimo y guardo
		postingsCompressed[p] = [compress(docs), compress(freqs)]

	# Descomprimo
	postings = collections.OrderedDict()
	for p in postingsCompressed:
		postings[p] = collections.OrderedDict()
		docsGapped = decompress(postingsCompressed[p][0])
		docsDecompressed = deltaDesencode(docsGapped)
		freqsDecompressed = decompress(postingsCompressed[p][1])
		for i in range(len(docsDecompressed)):
			postings[p][docsDecompressed[i]] = freqsDecompressed[i] + 0.0
	



if __name__ == "__main__":
	main()
