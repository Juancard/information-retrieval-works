# -*- coding: utf-8 -*-
import sys
import os
import shutil
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
		"term_min_size": 3,
		"term_max_size": 23
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

	sp = SequentialPostings.create(indexer.postings.getAll(), 
		path=INDEX_DIR, title="seq_posting.txt")
	print "Postings guardadas en: %s" % sp.path

	# Guardo configuracion del index
	CONFIG_NAME = "config.json"
	json.dump(indexConfig, open(INDEX_DIR + CONFIG_NAME,'w'))
	print "Configuracion en: %s" % (INDEX_DIR + CONFIG_NAME)

	postingsStats = indexer.postings.getStats()

	# sumo los tamanos de cada archivo dentro del directorio donde se aloja el indice 
	indexSize = sum(os.path.getsize(INDEX_DIR + f) for f in os.listdir("index_data") if os.path.isfile(INDEX_DIR + f))
	collectionSize = sum(os.path.getsize(f) for f in collection.allFiles())
	overhead = (indexSize / (float(collectionSize) + indexSize)) * 100
	with open("stats_" + collection.getName() + ".txt", "wt") as f:
		f.write("Coleccion: %s\n" % collection.getName())
		f.write("Listas de posteo:\n")
		f.write("\tTamano minimo: %d documentos\n" % postingsStats["min_len_posting"])
		f.write("\tTamano maximo: %d documentos\n" % postingsStats["max_len_posting"])
		f.write("\tTamano promedio: %.2f documentos\n" % postingsStats["mean_len_posting"])
		f.write("Tamano de la coleccion: %d bytes\n" % collectionSize)
		f.write("Tamano del indice: %d bytes\n" % indexSize)
		f.write("Overhead: %.2f%%\n" % overhead)
	print "Resultados finales en: %s" % "out.txt"
	
	print "Se elimina el indice"
	shutil.rmtree("index_data/")

if __name__ == "__main__":
	main()
