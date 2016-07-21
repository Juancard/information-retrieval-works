# -*- coding: utf-8 -*-
import sys
import os
import unicodedata
import string
import re

# Mi modulo para extraer expresiones regulares
from regex_tokenizer import RegexTokenizer

# Agrego al path la carpeta modulos
from directorio import Directorio

# ----------------------FUNCIONES ---------------------

def abrirArchivo(pathArchivo):
	# Chequeo si archivo existe
	try:
		archivo = open(pathArchivo)
		return archivo
	except NameError as er:
	    print pathArchivo + "- Name error({0}): {1}".format(e.errno, e.strerror)
	    return False
	except IOError as e:
	    print pathArchivo + "- I/O error({0}): {1}".format(e.errno, e.strerror)
	    return False

def orderByFrecuenceValueDescending(dic):
	return sorted(dic, key=lambda x: (dic[x]['cf'], dic[x]['df']), reverse=True)
def orderByFrecuenceValueAscending(dic):
	return sorted(dic, key=lambda x: (dic[x]['cf'], dic[x]['df']))

def tokenizar(linea):
	# Normalizo
	linea = linea.rstrip() # equivalente a chomp de perl
	linea = remove_accents(linea) # quito acentos
	linea = linea.lower() # mayusculas a minusculas
	linea = sacarPuntuacion(linea) # remuevo simbolos de puntuacion
	linea = quitarCaracteresRaros(linea) # quito otros caracteres
	lista_tokens = linea.split() # separo por espacio
	return lista_tokens

def sacarPalabrasVacias(listaTokens,listaVacias):
	lista = []
	for token in listaTokens:
		if token not in listaVacias:
			lista.append(token)
	return lista

def quitarAcentos(cadena):
	#NO ANDA
	#cadena = re.sub(r'[àáÀÁâä]', "a", cadena)
	#cadena = re.sub(r'[èéÈÉêë]', "e", cadena)
	#cadena = re.sub(r'[ìíÌÍîï]', "i", cadena)
	#cadena = re.sub(r'[òóÒÓôö]', "o", cadena)
	#cadena = re.sub(r'[ùúÙÚûü]', "u", cadena)
	return cadena

def remove_accents(input_str):
	encoding = "utf-8" # or iso-8859-15, or cp1252, or whatever encoding you use
	byte_string = b"café"  # or simply "café" before python 3.
	cadena = input_str.decode(encoding)
	nfkd_form = unicodedata.normalize('NFKD', cadena)
	out = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
	return out.encode("UTF-8")

def sacarPuntuacion(cadena):
	#cadena = cadena.encode('UTF-8')
	out = cadena.translate(string.maketrans("",""), string.punctuation)
	regex = re.compile('[%s]' % re.escape("¿¡"))
	out = regex.sub('',out)
	return out

def quitarCaracteresRaros(cadena):
	raros = "§âÂ¢«»­±¬ºï©®Ÿ€¾°“”·—’‘–Ã¼ü"
	regex = re.compile('[%s]' % re.escape(raros))
	return regex.sub('',cadena)

def isValidTermLength(token):	
	#Longitud de termino
	LONG_MIN_TERMINO = 3
	LONG_MAX_TERMINO = 23
	return len(token) >= LONG_MIN_TERMINO and len(token) <= LONG_MAX_TERMINO

def averageLengthKey(dic):
	lengthAllKeys = 0
	for key in dic:
		lengthAllKeys += len(key)
	return lengthAllKeys / (len(dic)+0.0)

def fileLengthByPath(path):
	return os.path.getsize(path)

# Para saber cuantos terminos aparecen X cantidad de veces
def countTermsOfGivenLength(dicTokens,givenLength):
	count = 0
	for key in dicTokens:
		if dicTokens[key]["cf"] == givenLength:
			count += 1
	return count

def getNthFirstTerms(dic,n):
	termsList = []
	for term in dic:
		if n == 0:
			return termsList
		termsList.append(term)
		n -= 1
			
def getStopwordsList(pathArchivo):
	listaVacias = []
	if os.path.isfile(str(pathArchivo)):
		stopwords = abrirArchivo(pathArchivo)
		if (stopwords):
			for line in stopwords:
				line = remove_accents(line.lower())
				listaVacias.extend(line.rstrip().split()) 
		stopwords.close()
	return listaVacias

# Pasa una lista de terminos al vocabulario y actualiza valores CF y DF
def updateVocabulario(listaTerminos, vocabulario, archivo):
	for termino in listaTerminos:
		if termino not in vocabulario:
			vocabulario[termino] = {"cf": 1, "df": 1}
			archivo["terms"].append(termino)
		else:
			vocabulario[termino]["cf"] += 1
			if termino not in archivo["terms"]:
				vocabulario[termino]["df"] += 1
				archivo["terms"].append(termino)
	return {
		"vocabulario": vocabulario,
		"archivo": archivo
	}

def printTerminos(vocabulario):
	terminosFile = open("terminos.txt", "w")
	terminosFile.write("-"*50+"\n")
	terminosFile.write("\tTERMINOS \tpor Juan Cardona\n")
	terminosFile.write("-"*50+"\n")
	terminosFile.write("TERMINO - FRECUENCIA - DF:\n")
	for k in orderByFrecuenceValueDescending(vocabulario):
		terminosFile.write("%s - %d - %d\n" % (k,vocabulario[k]["cf"],vocabulario[k]["df"]))
	terminosFile.close()

def printEstadisticas(estadisticas):
	estadisticasFile = open("estadisticas.txt", "w")
	s = []
	s.append("-"*50+"\n")
	s.append("\tESTADISTICAS \tpor Juan Cardona\n")
	s.append("-"*50+"\n")
	s.append("Cantidad de Documentos Procesados: %d\n" 
		% estadisticas["cant_documentos"])
	s.append("Cantidad de Tokens Extraidos: %d\n" 
		% estadisticas["cant_tokens"])
	s.append("Cantidad de Términos Extraidos: %d\n" 
		% estadisticas["cant_terminos"])
	s.append("Cantidad Promedio de Tokens por Documento: %.2f\n" 
		% estadisticas["promedio_tokens_por_doc"])
	s.append("Cantidad Promedio de Términos por Documento: %.2f\n" 
		% estadisticas["promedio_terminos_por_doc"])
	s.append("Largo promedio de un término: %.2f\n" 
		% estadisticas["largo_promedio_termino"])
	s.append("Cantidad de tokens del documento más corto: %d\n" 
		% estadisticas["cant_tokens_doc_corto"])
	s.append("Cantidad de términos del documento más corto: %d\n" 
		% estadisticas["cant_terminos_doc_corto"])
	s.append("Cantidad de tokens del documento más largo: %d\n" 
		% estadisticas["cant_tokens_doc_largo"])
	s.append("Cantidad de términos del documento más largo: %d\n" 
		% estadisticas["cant_terminos_doc_largo"])
	s.append("Cantidad de términos que aparecen 1 vez en la colección: %d\n" 
		% estadisticas["terminos_frecuencia_uno"])
	estadisticasFile.write(''.join(s))
	estadisticasFile.close()

def printRanking(data):
	rankingFile = open("ranking.txt", "w")
	
	s = []
	s.append("-"*50+"\n")
	s.append("\tRANKING \tpor Juan Cardona\n")
	s.append("-"*50+"\n")
	
	s.append("LOS %d TÉRMINOS MÁS FRECUENTES\n" % data["nthTerm"])
	s.append("\n\tTERMINO - CF\n")
	maxCFList = getNthFirstTerms(orderByFrecuenceValueDescending(data["vocabulario"]), data["nthTerm"])
	for term in maxCFList:
		s.append("\t%s - %d\n" % (term,data["vocabulario"][term]["cf"]))
	
	minCFList = getNthFirstTerms(orderByFrecuenceValueAscending(data["vocabulario"]), data["nthTerm"])
	s.append("\nLOS %d TÉRMINOS MENOS FRECUENTES\n" % data["nthTerm"])
	s.append("\n\tTERMINO - CF\n")
	for term in minCFList:
		s.append("\t%s - %d\n" % (term,data["vocabulario"][term]["cf"]))
	
	rankingFile.write(''.join(s))
	rankingFile.close()
# -----------------------------------------------------
if __name__ == "__main__":
	pass