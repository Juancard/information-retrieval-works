# -*- coding: utf-8 -*-
import re
import codecs

class Query(object):

	OPERATOR_AND = "AND"
	OPERATOR_OR = "OR"
	OPERATOR_NOT = "NOT"
	OPERATOR_ADJACENT = "ADJACENT"
	OPERATOR_CLOSE = "CLOSE-TO"
	OPERATOR_DISTANCE = "N-TERMS"
	OPERATOR_PHRASE = '"'
	booleanOperators = [OPERATOR_AND, OPERATOR_OR, OPERATOR_NOT]
	positionalOperators = [OPERATOR_ADJACENT, OPERATOR_CLOSE, OPERATOR_DISTANCE]

	def __init__(self, num, title):
		self.num = num
		self.title = title
		self.terms = []
		self.bagOfWords = {}
		self.setOfWords = set()
		self.booleanOperator = False
		self.positionalOperator = False
		self.phraseOperator = False

	def setBooleanOperator(self):
		for bo in self.booleanOperators:
			if bo in self.title:
				self.booleanOperator = bo 
				self.title = self.title.replace(bo, "")

	def setPositionalOperator(self):
		for po in self.positionalOperators:
			if po == self.OPERATOR_DISTANCE:
				pattern = re.compile(r".*\s((\d+)-TERMS)")
				m = pattern.match(self.title)
				if m:
					self.positionalOperator = int(m.groups()[1])
					self.title = self.title.replace(m.groups()[0], "")
			elif po in self.title:
				self.positionalOperator = po 
				self.title = self.title.replace(po, "")

	def setPhraseOperator(self):
		pattern = re.compile(r'.*\s*"(.*)"')
		m = pattern.match(self.title)
		if m:
			self.title = m.groups()[0]
			self.phraseOperator = True

	def normalize(self, lexAnalyser):
		return lexAnalyser.analyse(self.title)["terms"]

	def setBagOfWords(self, terms):
		for t in terms:
			if t in self.bagOfWords:
				self.bagOfWords[t] += 1
			else:
				self.bagOfWords[t] = 1

	def setSetOfWords(self, terms):
		self.setOfWords = set(terms)

	def __repr__(self):
		return self.title.encode("UTF-8") + ": " + repr(self.bagOfWords)

class QueriesManager(object):

	def __init__(self, booleanOperators = False,
		positionalOperators = False, phraseOperator = False):
		
		if model is not None:
			self.model = model
		self.booleanOperators = booleanOperators
		self.positionalOperators = positionalOperators
		self.phraseOperator = phraseOperator
		self.queries = []
		self.lexAnalyser = False

	def setLexAnalyser(self, lexAnalyser):
		self.lexAnalyser = lexAnalyser

	def addQuery(self, query):
		if self.booleanOperators:
			query.setBooleanOperator()
		if self.positionalOperators:
			query.setPositionalOperator()			
		if self.phraseOperator:
			query.setPhraseOperator()

		terms = []
		if self.lexAnalyser:
			terms = query.normalize(self.lexAnalyser)
		else:
			terms = query.title.split(" ")
		query.terms = terms

		self.queries.append(query)

	def setQueriesFromConsole(self):
		if self.booleanOperators:
			print "\nQueries booleanas permitidas:\n\ttermino1 AND termino2\n\ttermino1 OR termino2\n\tNOT termino1"
		if self.positionalOperators:
			print "\nQueries posicionales permitidas:"
			for op in Query.positionalOperators:
				print "\ttermino1 %s termino2" % op
		if self.phraseOperator:
			print '\nBusqueda por Frase con operador \'"\'\nEjemplo: "base de datos"'

		qId = 1
		qInput = raw_input("Ingresar query %d (-1 para salir): " % qId).decode("UTF-8") 
		while qInput != "-1":
			q = Query(qId, qInput)
			self.addQuery(q)
			qId += 1
			qInput = raw_input("Ingresar query %d (-1 para salir): " % qId).decode("UTF-8")


	def setQueriesFromTrecFile(self, path):

		def getMatch(line, pattern):
			out = []
			m = pattern.match(line)
			if m:
				out = m.groups()
			return out

		pattern = re.compile(r"\s*(?:<(/?[a-zA-Z]+)>)(?:(.+)<(/[a-zA-Z]+)>)?")
		
		with codecs.open(path, mode='rt', encoding='utf-8') as f:
			isNewQuery = False
			numQuery = False
			title = False
			for line in f:
				values = getMatch(line, pattern)
				if values[0].lower() == "top":
					isNewQuery = True
				if values[0].lower() == "num" and values[2].lower() == "/num":
					numQuery = values[1]
				if values[0].lower() == "title" and values[2].lower() == "/title":
					title = values[1]
				if values[0].lower() == "/top":
					if isNewQuery and numQuery and title:
						q = Query(int(numQuery), title)
						self.addQuery(q)
					isNewQuery = False
					numQuery = False
					title = False

