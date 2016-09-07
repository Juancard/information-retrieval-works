# -*- coding: utf-8 -*-
import sys
import os

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
from Collection import Collection
from Indexer import Indexer

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

	indexer = Indexer(collection)
	indexer.index(indexConfig)

	print "%s: generado correctamente" % indexer.printStatsFile("estadisticas.txt")
	print "%s: generado correctamente" % indexer.vocabulary.printTopKFile("top_k.txt", 10)
	print "%s: generado correctamente" % indexer.vocabulary.printTermsFile("terminos.txt")


if __name__ == "__main__":
	main()
