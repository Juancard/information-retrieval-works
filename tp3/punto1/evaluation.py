# -*- coding: utf-8 -*-

#
# EVALUATION.PY
#
# ESTE SCRIPT RECIBE COMO PARAMETROS EL PATH AL ARCHIVO 
# RECUPERADO ṔOR RETRIEVAL.PY Y OTRO PATH AL ARCHIVO DE 
# JUICIOS DE RELEVANCIA.  
# DEVUELVE UN TXT CON LAS ESTADISTICAS DE LA EVALUACION
#
#

import sys
import os
import re
from collections import defaultdict

#-------------------FUNCTIONS------------------

def getParameters():
	for i in range(1,2):
		try:
			sys.argv[i]
			if not(os.path.isfile(sys.argv[i])):
				print "Error en parametro %d. Path no válido" % (i) 
				sys.exit()
		except IndexError:
			print "Uso:"
			print "%s /path/to/retrieved.txt /path/to/relevantDocs.txt" % sys.argv[0]
			print "Ejemplo:"
			print "%s " % sys.argv[0],
			print "/home/user/tp2/punto1/booleanModel.txt /home/user/corpus/ejemploRibeiro/relevantDocs.txt"
			sys.exit()
	return sys.argv[1:3]

# donde formato de archivo es:
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

# Estructura:
# query1: 
# 	Rank1: docId
#	Rank2: docId
#	(...)
#	RankN: docId
# (...)
# queryN: 
# 	(...)
def getRetrieved(path):
	retrieved = {}
	with open(path) as f:
		next(f) # salteo header
		for linea in f:
			if linea:
				linea = linea.rstrip().split()
				if len(linea) >= 3:
					if int(linea[0]) not in retrieved:
						retrieved[int(linea[0])] = {}
					retrieved[int(linea[0])][int(linea[1])] = int(linea[2])
	return retrieved

# Estructura:
# query1: [docId1, docId2, ..., docIdN]
# (...)
# queryN: [docId1, docId2, ..., docIdN]
def getRelevant(path):
	relevantDocs = {}
	relevantRead = readVectorFile(path)
	for queryId, docsString in relevantRead:
		relevantDocs[int(queryId)] = [int(doc) for doc in docsString.split(",")]
	return relevantDocs

# CAlcula precision y recall para cada doc de retrieved 
# segun docs en relevant
def getRP(retrieved, relevant):
	totalRelevant = len(relevant)
	retrievedAcum = 0.0
	relevantRetrievedAcum = 0.0
	evaluation = {}
	for rank in retrieved:
		retrievedAcum += 1.0
		isRelevant = retrieved[rank] in relevant
		if isRelevant:
			relevantRetrievedAcum += 1.0
		evaluation[rank] = {
			"is_relevant": isRelevant,
			"precision": relevantRetrievedAcum / retrievedAcum,
			"recall": relevantRetrievedAcum / totalRelevant
		}
	return evaluation

# Funcion que devuelve una matriz 
# 'recall standard' vs 'precision interpolada'  
def getRpInterpolated(rp):
	out = {}
	recallStd = 0.0
	end = 1.0
	step = 0.1
	while recallStd <= end:
		aux = recallStd
		precisionList = [rp[r]["precision"] for r in rp if rp[r]["recall"] >= aux and rp[r]["recall"] < round(aux + step,1)]
		while not precisionList and aux < end:
			aux += step
			precisionList = [rp[r]["precision"] for r in rp if rp[r]["recall"] >= aux and rp[r]["recall"] < round(aux + step, 1)]
		if not precisionList:
			previousRecall = round(recallStd - step, 1)
			try:
				out[recallStd] = out[previousRecall]
			except KeyError:
				out[recallStd] = 0.0
		else:
			out[recallStd] = max(precisionList)			
		recallStd = round(recallStd + step, 1)
	return out

def getStats(rp, relevant):
	out = {}
	relRetrPrec = [rp[r]["precision"] for r in rp if rp[r]["is_relevant"]]
	out["retrieved"] = len(rp)
	out["relevant"] = len(relevant)
	out["relevant_retrieved"] = len(relRetrPrec)
	out["average_precision"] = sum(relRetrPrec) / len(relRetrPrec)
	out["r_precision"] = rp[len(relevant)]["precision"] if len(relevant) < len(rp) else rp[len(rp)]["precision"]
	return out

def getEvaluation(retrieved, relevant):
	evaluation = {}
	for q in retrieved:
		evaluation[q] = {}
		evaluation[q]["rp"] = getRP(retrieved[q], relevant[q])
		evaluation[q]["rp_int"] = getRpInterpolated(evaluation[q]["rp"])
		evaluation[q]["stats"] = getStats(evaluation[q]["rp"], relevant[q])
	return evaluation

# Se toman todas las evaluaciones de las queries 
# y se genera una evaluación general
def getGeneralEvaluation(e):
	def getGeneralStats(e):
		return {
			"totalQueries": len(e),
			"retrieved": sum([e[q]["retrieved"] for q in range(len(e))]),
			"relevant": sum([e[q]["relevant"] for q in range(len(e))]),
			"relevant_retrieved": sum([e[q]["relevant_retrieved"] for q in range(len(e))]),
			"average_precision": sum([e[q]["average_precision"] for q in range(len(e))]) / len(e),
			"r_precision": sum([e[q]["r_precision"] for q in range(len(e))]) / len(e)
		}
	def getGeneralRP(e):
		rp = {}
		maxRank = max([len(e[i]) for i in range(len(e))])
		for rank in range(1, maxRank + 1):
			precisionOnRank = [e[q][rank]["precision"] for q in range(len(e)) if rank in e[q]]
			rp[rank] = {
				"precision": sum(precisionOnRank) / len(precisionOnRank)
			}
		return rp
	def getGeneralRPInt(e):
		rpInt = defaultdict(int)
		for i in range(len(e)):
			for recStd in e[i]:
				rpInt[recStd] += (e[i][recStd] / len(e))
		return rpInt

	out = {}
	out["stats"] = getGeneralStats([e[q]["stats"] for q in e])
	out["rp"] = getGeneralRP([e[q]["rp"] for q in e])
	out["rp_int"] = getGeneralRPInt([e[q]["rp_int"] for q in e])

	return out

# evaluacion de todas las queries juntas. 
# NO USAR. Data pocoŕepresentativa
def getSingleEvaluationForAllQueries(retrieved, relevant):
	totalRelevant = sum(len(relevant[q]) for q in relevant)
	retrievedAcum = 0.0
	retrievedRelevantAcum = 0.0
	# Valor que al dividirlo por los relevantes recuperados
	# devuelve el avg precision
	precisionOnRelevantAcum = 0.0
	rank = 0.0
	out = {
		"rp": {},
		"stats": {}
	}
	for q in retrieved:
		for r in retrieved[q]:
			retrievedAcum += 1.0
			rank += 1
			isRelevant = retrieved[q][r] in relevant[q]
			if isRelevant:
				retrievedRelevantAcum += 1.0
				precisionOnRelevantAcum += retrievedRelevantAcum / retrievedAcum
			out["rp"][rank] = {
				"is_relevant": isRelevant,
				"precision": retrievedRelevantAcum / retrievedAcum,
				"recall": retrievedRelevantAcum / totalRelevant
			}
	out["stats"] = {
		"totalQueries": len(retrieved),
		"retrieved": retrievedAcum,
		"relevant": totalRelevant,
		"relevant_retrieved": retrievedRelevantAcum,
		"average_precision": precisionOnRelevantAcum / retrievedRelevantAcum,
		"r_precision": out["rp"][totalRelevant]["precision"]
	}
	return out

def printEvaluationFile(e):
	fileName = "results.eval"
	with open(fileName, "w") as f:
		s = []
		s.append("_"*36+"\n")
		s.append("Number of queries = %d\n" % e["stats"]["totalQueries"])
		s.append("Retrieved = %d\n" % e["stats"]["retrieved"])
		s.append("Relevant = %d\n" % e["stats"]["relevant"])
		s.append("Relevant retrieved = %d\n" % e["stats"]["relevant_retrieved"])
		s.append("_"*36+"\n")
		s.append("Average Precision: %.4f\n" % e["stats"]["average_precision"])
		s.append("R Precision: %.4f\n" % e["stats"]["r_precision"])
		s.append("_"*36+"\n")
		for v in [(r, e["rp"][r]["precision"]) for r in sorted(e["rp"])]:
			s.append("Precision at %d: %.4f\n" % v)
		s.append("_"*36+"\n")
		for v in [(r * 100, e["rp_int"][r]) for r in sorted(e["rp_int"])]:
			s.append("Precision at %d%%: %.4f\n" % v)
		s.append("_"*36+"\n")
		s.append("Average Precision: %.4f\n" % e["stats"]["average_precision"])
		f.write("".join(s))
	return fileName
#--------------------END FUNCTIONS-------------------

parameters = getParameters()

pathRetrieved = parameters[0]
pathRelevant = parameters[1]

relevant = getRelevant(pathRelevant)
retrieved = getRetrieved(pathRetrieved)

# OBTENGO RP Y STATS DE LA EVALUACION DE CADA QUERY
evaluation = getEvaluation(retrieved, relevant)

# MISMOS DATOS PERO PARA TODAS LAS QUERIES EN CONJUNTO
generalEvaluation = getGeneralEvaluation(evaluation)

# GENERO ARCHIVO DE SALIDA 
print "---\nEvaluation results saved as %s\n---" % (printEvaluationFile(generalEvaluation))