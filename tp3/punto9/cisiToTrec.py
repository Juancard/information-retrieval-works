# -*- coding: utf-8 -*-
import sys
import os
import re

# ----------------------FUNCIONES ---------------------#

def newTrecDocument(dic):
	if dic:
		with open("collection_output.trec", "a") as trecFile:
			s = []
			s.append("<DOC>"+"\n")
			s.append("<DOCNO> "+str(dic["id"])+" </DOCNO>\n")
			s.append(dic["body"])
			s.append("</DOC>"+"\n")
			trecFile.write(''.join(s))

def loadTagToDic(dic, tag, value):
	if value:
		dic[tag] = value
	return dic

def menu():
	#Obtengo archivo cisi
	try:
		path = sys.argv[1]
		if not(os.path.isfile(sys.argv[1])):
			print "Path a Archivo no es válido"
			sys.exit()
	except IndexError:
		print """Uso:
	{0} /path/to/cisi_file.all
Ejemplo:
	{0} /CISI.ALL""".format(sys.argv[0])
		sys.exit()

	with open(path) as cisiFile:

		# Guardo datos de cada documento
		documentDic = {}

		# CUando linea no es un tag lo guardo aqui
		aux = ""

		# Elimino archivo generado por anterior 
		# corrida de este programa
		try:
			os.remove("collection_output.trec")
		except OSError:
			pass

		for linea in cisiFile:

			if linea.startswith(".I", 0, 2):
				# Creo el documento anterior
				dic = loadTagToDic(documentDic, "x", aux)
				aux = ""
				newTrecDocument(documentDic)

				# Tomo id del documento nuevo
				documentDic["id"] = int(linea.split(" ")[1])

			elif linea.startswith(".T", 0, 2):
				#print "esTitulo"
				pass
			
			elif linea.startswith(".A", 0, 2):
				#print "esAutor"
				dic = loadTagToDic(documentDic, "title", aux)
				aux = ""
			
			elif linea.startswith(".W", 0, 2):
				#print "escUERPO"
				dic = loadTagToDic(documentDic, "author", aux)
				aux = ""
			
			elif linea.startswith(".X", 0, 2):
				#print "esX"
				dic = loadTagToDic(documentDic, "body", aux)
				aux = ""
			
			else:
				aux += linea

		# Creo el ultimo documento
		dic = loadTagToDic(documentDic, "x", aux)
		newTrecDocument(documentDic)

# -----------------------------------------------------
if __name__ == "__main__":
	menu()