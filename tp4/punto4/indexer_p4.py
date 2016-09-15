# -*- coding: utf-8 -*-
import sys
import os
import json

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../../modulos"))
from Collection import Collection
from Indexer import Indexer
from PicklePersist import PicklePersist
from Postings import SequentialPostings

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
		# SIN MINIMOS Y MAXIMOS PARA RECUPERAR POR POSICIONES
		#"term_min_size": 3,
		#"term_max_size": 23
	}
	
	# Indexo
	indexer = Indexer(collection)
	indexer.index(indexConfig)

	# Persisto indice para su recuperacion
	INDEX_DIR = "index_data/"
	if not os.path.exists(INDEX_DIR):
	    os.makedirs(INDEX_DIR)

	pp = PicklePersist()
	print "Vocabulario guardado en: %s" % pp.save(indexer.vocabulary, INDEX_DIR + "vocabulary")
	print "Documentos guardados en: %s" % pp.save(indexer.documents, INDEX_DIR + "documents")

	spFreq = SequentialPostings.create(indexer.postings.getAll(), 
		path=INDEX_DIR, title="seq_freq_posting.txt")
	print "Postings con frecuencias guardadas en: %s" % spFreq.path

	spPosition = SequentialPostings.create(indexer.positions.getAll(), 
		path=INDEX_DIR, title="seq_position_posting.txt")
	print "Postings posicionales guardadas en: %s" % spPosition.path


	# Guardo configuracion del index
	CONFIG_NAME = "config.json"
	json.dump(indexConfig, open(INDEX_DIR + CONFIG_NAME,'w'))
	print "Configuracion en: %s" % (INDEX_DIR + CONFIG_NAME)

if __name__ == "__main__":
	main()
