# -*- coding: utf-8 -*-

import sys
import codecs
from LexAnalyser import LexAnalyser
from Vocabulary import Vocabulary
from Postings import DictionaryPostings
from Documents import Documents

class Indexer(object):

	def __init__(self, collection):
		self.collection = collection
		self.lexAnalyser = False
		self.stats = self.getInitStats()
		self.vocabulary = Vocabulary()
		self.postings = DictionaryPostings({})
		self.documents = Documents()
		self.documentsTerms = {}
		self.positions = DictionaryPostings({})

	def index(self, config):
		"""Indexa la coleccion dada"""

		# Configuro el analizador lexico
		self.lexAnalyser = LexAnalyser(config)

		#-----------------LEER-COLECCION--------------#
		docId = 0
		for fileName in self.collection.onlyFiles():

			# Guardo los datos del archivo actual
			actualDoc = {
				"name": fileName,
				"path": self.collection.path + fileName
			} 	

			#----------LEER-ARCHIVO--------------------#

			print "Cargando "+actualDoc["name"]
			with codecs.open(actualDoc["path"], mode='rt', encoding='utf-8') as f:
				
				# GUardo tokens y terminos del documento
				tokens = []
				terms = []

				for line in f:
					# Aplica tokenizado, stopwords y demas (segun config)
					analysed = self.lexAnalyser.analyse(line)
					terms.extend(analysed["terms"])
					tokens.extend(analysed["tokens"])

			# Guardo documento actual
			docId += 1
			self.documents.addDocument(docId, actualDoc["name"])
			
			# De cada documento los terminos que tiene (sin repetir)
			self.documentsTerms[docId] = set()

			# Actualizo vocabulario
			self.updateIndex(docId, terms)
			#Actualizo stats
			self.updateStats(tokens, terms)

			#------FIN-LEER-ARCHIVO--------------------#
		
		#----------------FIN-LEER-COLECCION---------#
		print "Generando stats"
		self.endStats()
		print u"Ordenando vocabulario alfabéticamente"
		self.vocabulary.setAlphabeticalOrder()
		print u"Generando id de los términos"
		self.setTermsId()
		self.postings.sortByKey()
		self.positions.sortByKey()

	def updateIndex(self, docId, terms):
		position = 0
		for t in terms:
			self.documentsTerms[docId].add(t)
			# Si termino no esta en vocabulario lo agrego inicializando la data
			if not self.vocabulary.isATerm(t):
				self.vocabulary.addTerm(t, 1.0, 1.0)
				self.postings.addPosting(t, docId, 1.0)
				self.positions.addPosting(t, docId, [position])
			else:
				self.vocabulary.incrementCF(t, 1.0)
				# termino no estaba en este documento?
				if not self.postings.isDocInPosting(t, docId):
					self.vocabulary.incrementDF(t, 1.0)
					self.postings.addDocToPosting(t, docId, 1.0)
					self.positions.addDocToPosting(t, docId, [position])
				# else termino ya existe en documento:
				else:
					# Actualizo postings con frecuencias
					self.postings.addDocToPosting(t, docId, self.postings.getValue(t, docId) + 1.0)
					# Actualizo postings posicionales
					positionList = self.positions.getValue(t, docId)
					positionList.append(position)
					self.positions.addDocToPosting(t, docId, positionList)
			position += 1

	def setTermsId(self):
		termId = 1
		for term in self.vocabulary.content:
			self.vocabulary.setId(term, termId)
			self.postings.termToId(term, termId)
			self.positions.termToId(term, termId)
			for doc in self.documentsTerms:
				if term in self.documentsTerms[doc]:
					self.documentsTerms[doc].discard(term)
					self.documentsTerms[doc].add(termId)  
			termId += 1

	def getInitStats(self):
		out = {
			"tokens_count": 0.0,
			"terms_count": 0.0,
			"docs_count": 0.0,
			"longestDoc": {
				"tokens_count": -1,
				"terms_count": -1
			},
			"shortestDoc": {
				"tokens_count": sys.maxint,
				"terms_count": sys.maxint
			}
		}
		return out

	def updateStats(self, tokens, terms):
		tokensLength = len(tokens)
		termsLength = len(set(terms))

		self.stats["tokens_count"] += tokensLength
		self.stats["docs_count"] += 1.0

		# Documento es el mas grande?
		if tokensLength >= self.stats["longestDoc"]["tokens_count"]:
			self.stats["longestDoc"]["tokens_count"] = tokensLength
			self.stats["longestDoc"]["terms_count"] = termsLength
		# Documento es el mas pequeno?
		if tokensLength <= self.stats["shortestDoc"]["tokens_count"]:
			self.stats["shortestDoc"]["tokens_count"] = tokensLength
			self.stats["shortestDoc"]["terms_count"] = termsLength

	def endStats(self):
		self.stats["terms_count"] = len(self.vocabulary.content)
		self.stats["avg_tokens_by_doc"] = self.stats["tokens_count"] / self.stats["docs_count"]
		self.stats["avg_terms_by_doc"] = self.stats["terms_count"] / self.stats["docs_count"]
		self.stats["avg_term_length"] = sum([len(key) for key in self.vocabulary.content]) / (len(self.vocabulary.content) + 0.0)
		self.stats["terms_freq_one"] = len([key for key in self.vocabulary.content if self.vocabulary.getCF(key) == 1])


	def printStatsFile(self, title):
		with open(title, "w") as statsFile:
			s = []
			s.append("-"*50+"\n")
			s.append("\tESTADISTICAS \tpor Juan Cardona\n")
			s.append("-"*50+"\n")
			s.append("Cantidad de Documentos Procesados: %d\n" 
				% self.stats["docs_count"])
			s.append("Cantidad de Tokens Extraidos: %d\n" 
				% self.stats["tokens_count"])
			s.append("Cantidad de Términos Extraidos: %d\n" 
				% self.stats["terms_count"])
			s.append("Cantidad Promedio de Tokens por Documento: %.2f\n" 
				% self.stats["avg_tokens_by_doc"])
			s.append("Cantidad Promedio de Términos por Documento: %.2f\n" 
				% self.stats["avg_terms_by_doc"])
			s.append("Largo promedio de un término: %.2f\n" 
				% self.stats["avg_term_length"])
			s.append("Cantidad de tokens del documento más corto: %d\n" 
				% self.stats["shortestDoc"]["tokens_count"])
			s.append("Cantidad de términos del documento más corto: %d\n" 
				% self.stats["shortestDoc"]["terms_count"])
			s.append("Cantidad de tokens del documento más largo: %d\n" 
				% self.stats["longestDoc"]["tokens_count"])
			s.append("Cantidad de términos del documento más largo: %d\n" 
				% self.stats["longestDoc"]["terms_count"])
			s.append("Cantidad de términos que aparecen 1 vez en la colección: %d\n" 
				% self.stats["terms_freq_one"])
			statsFile.write(''.join(s))
		return title