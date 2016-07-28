# -*- coding: utf-8 -*-
import sys
import os
import unicodedata
import string

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../modulos"))
from directorio import Directorio
import lex_analyser

if __name__ == "__main__":

	#Obtengo path
	try:
		path = sys.argv[1]
		if not(os.path.isdir(sys.argv[1])):
			print "Path no válido"
			sys.exit()
		if not path.endswith('/'):
			path += '/'
	except IndexError:
		print """Uso:
	{0} /path/a/corpus [/path/to/stop-words.txt]
Ejemplos:
	{0} ../corpus/T12012-gr stopwords.txt
	{0} ../corpus/T12012-gr""".format(sys.argv[0])
		sys.exit()

	# Obtengo Stopwords
	try:
		stopwords = sys.argv[2]
		file = lex_analyser.abrirArchivo(stopwords)
		if not(file):
			sys.exit()
		else: 
			file.close()
	except IndexError:
		stopwords = False

	# obtengo lista de stopwords
	listaVacias = lex_analyser.getStopwordsList(stopwords)
	
	vocabulario = {}

	# Contadores para tokens y terminos extraidos
	tokensCounter = 0
	termCounter = 0

	# Guardo data del archivo mas grande y mas pequeno
	# Valores ficticios en length 
	# para comparar con mayor y menor documento
	longestFileDic = {
		"length": -sys.maxint -1
	}
	shortestFileDic = {
		"length": sys.maxint
	}

	# Obtengo archivos del directorio
	archivos = Directorio(path).onlyFiles()

	for nombreArchivo in archivos:

		# Guardo los datos del archivo actual
		archivoDic = {
			"name": nombreArchivo,
			"path": path + nombreArchivo,
			"terms": [],
			"token_count": 0,
			"term_count": 0
		} 
		# Abro archivo actual
		archivoDic["file"] = lex_analyser.abrirArchivo(archivoDic["path"])
		# Calculo tamano
		archivoDic["length"] = lex_analyser.fileLengthByPath(archivoDic["path"])

		print "Cargando "+archivoDic["name"]

		# Si uno de los archivos no pudo abrirse salgo del programa
		if not(archivoDic["file"]):
			sys.exit()

		for linea in archivoDic["file"]:

			# Normalizo y tokenizo
			listaTokens = lex_analyser.tokenizar(linea)

			# Tomo estadisticas de tokens
			# Contador de solo los tokens del archivo actual
			archivoDic["token_count"] += len(listaTokens)
			# Contador de todos los tokens del corpus
			tokensCounter += len(listaTokens)

			# Quito palabras vacias
			listaTokens = lex_analyser.sacarPalabrasVacias(listaTokens, listaVacias)

			# Selecciono terminos de longitud valida
			listaTerminos = [token for token in listaTokens if lex_analyser.isValidTermLength(token)]
			
			# Tomo estadisticas de terminos
			# contador de todos los terminos del corpus
			termCounter += len(listaTerminos)
			# contador de solo los terminos del archivo actual
			archivoDic["term_count"] += len(listaTerminos)

			# Agrega terminos a vocabulario y 
			# actualiza valores de DF y CF
			resultado = lex_analyser.updateVocabulario(listaTerminos, vocabulario, archivoDic)
			vocabulario = resultado["vocabulario"]
			archivoDic = resultado["archivo"]
			
		#-----FIN-LEER-LINEA-ARCHIVO---------

		# Archivo es el mas grande?
		if archivoDic["length"] >= longestFileDic["length"]:
			longestFileDic = archivoDic

		# Archivo es el mas pequeno?
		if archivoDic["length"] <= shortestFileDic["length"]:
			shortestFileDic = archivoDic

		archivoDic["file"].close()

	#------FIN-ARCHIVO----------

	# TERMINOS.TXT
	lex_analyser.printTerminos(vocabulario)

	# ESTADISTICAS.TXT
	estadisticas = {
		"cant_documentos": len(archivos),
		"cant_tokens": tokensCounter,
		"cant_terminos": termCounter,
		"promedio_tokens_por_doc": tokensCounter / (len(archivos) + 0.0),
		"promedio_terminos_por_doc": termCounter / (len(archivos) + 0.0),
		"largo_promedio_termino": lex_analyser.averageLengthKey(vocabulario),
		"cant_tokens_doc_corto": shortestFileDic["token_count"],
		"cant_terminos_doc_corto": shortestFileDic["term_count"],
		"cant_tokens_doc_largo": longestFileDic["token_count"],
		"cant_terminos_doc_largo": longestFileDic["term_count"],
		"terminos_frecuencia_uno": lex_analyser.countTermsOfGivenLength(vocabulario,1)
	}
	lex_analyser.printEstadisticas(estadisticas)

	# RANKING.TXT
	data = {
		"nthTerm": 10,
		"vocabulario": vocabulario
	}
	lex_analyser.printRanking(data)
