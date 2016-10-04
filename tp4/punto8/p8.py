# -*- coding: utf-8 -*-

############## p8.py ##################
# Script que lee archivo dump_10k.txt

###############################################

import sys
import os
import codecs
import collections
import time
import struct
import numpy as np

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
	start = time.time()
	with open("binary_postings.dat", mode='wb') as postingsFile:
		with codecs.open(corpusTxt, mode='rt', encoding='utf-8') as dumpFile:
			termId = 1; pointer = 0
			for line in dumpFile:

				# Separo elementos de la linea
				term, df, docs = line.rstrip().split(":")
				df = int(df)

				print "Cargando: ",term
				
				# Cargando data del vocabulario
				vocabulary[term] = {
					"id": termId,
					"df": df,
					"pointer": pointer,
					"skip_list": collections.OrderedDict()
				}

				# Tomo docs id de la actual linea del archivo
				docs = docs.split(",")
				for i in range(len(docs)):
					try: docs[i] = int(docs[i])
					except ValueError: del docs[i]

				# Ordeno docs
				docs = sorted(docs)

				# Genero skip list
				#
				# formato:
				# skip[d] = p
				#
				# donde, 
				# p = puntero a documento
				# d = documento anterior a p
				#
				# ESto se hace para facilitar la tarea de decodificar deltaencode
				# Biblio: search engine, 2015, pagina 177
				#
				if df < 2: totalSkipPointers = df
				else: totalSkipPointers = int(np.sqrt(df)) + 1
				step = df / totalSkipPointers
				actualPos = step - 1
				for i in range(totalSkipPointers):
					previousPos = actualPos - 1
					if previousPos < 0:
						previousPos = 0
					vocabulary[term]["skip_list"][docs[previousPos]] = pointer + (actualPos * 4)
					actualPos += step

				# dgapeo
				previousValue = docs[0]
				for i in range(1, len(docs)):
					aux = docs[i]
					docs[i] = docs[i] - previousValue
					previousValue = aux

				# Escribo posting binaria
				postingsFile.write(struct.pack('<%sI' % df, *docs))
				postingsFile.write(struct.pack('<%sf' % df, *([1] * int(df))))
				
				pointer += df * 4 * 2
				termId += 1

	print "time:",time.time() - start
	print termId

# funcion para chequear que posting se creo correctamente
def testBinaryFile(vocabulary):
	with open("binary_postings.dat", "rb") as f:
		for term in vocabulary:

			# Me posiciono en el termino
			f.seek(vocabulary[term]["pointer"])

			# Leo longitud de documents Id
			lenDocs = vocabulary[term]["df"]

			# Leo documents ids
			bDocs = f.read(lenDocs * 4)
			docIds = struct.unpack('<%iI' % lenDocs, bDocs)

			# Leo frecuencias
			bFreqs = f.read(lenDocs * 4)
			freqs = struct.unpack('<%if' % lenDocs, bFreqs)

			print freqs

# funcion para chequear que dgaps se creo correctamente
def testDgaps(vocabulary):
	out = []
	with open("binary_postings.dat", "rb") as f:
		for term in vocabulary:
			f.seek(vocabulary[term]["pointer"])
			df = vocabulary[term]["df"]
			dgapped = 0
			for i in range(df):
				dgapped += struct.unpack('<I', f.read(4))[0]
				out.append(dgapped)
	print "Dgap: ", out
# funcion para chequear que skip list se creo correctamente
def testSkip(vocabulary):
	out = []
	with open("binary_postings.dat", "rb") as f:
		for term in vocabulary:
			for doc in vocabulary[term]["skip_list"]:
				f.seek(vocabulary[term]["skip_list"][doc])
				docRead = struct.unpack('<I', f.read(4))[0]
				out.append(doc + docRead)
	print "Skip: ", out

if __name__ == "__main__":
	main()