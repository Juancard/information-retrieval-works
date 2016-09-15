# -*- coding: utf-8 -*-

class BooleanRetriever(object):
	"""Realiza recuperaciones en base al modelo booleano"""
	def __init__(self, vocabulary, postings, documents):
		self.vocabulary = vocabulary
		self.postings = postings
		self.documents = documents

	def retrieve(self, queries):
		retrieved = {}
		for q in queries:
			if q.positionalOperator:
				retrieved[q.num] = self.positionalRetrieve(q)
			elif q.booleanOperator:
				retrieved[q.num] = self.booleanRetrieve(q)
			else:
				retrieved[q.num] = self.union(q.setOfWords)
		return retrieved

	def booleanRetrieve(self, query):
		terms = query.setOfWords
		bo = query.booleanOperator

		if bo == query.OPERATOR_AND:
			retrieved = self.intersect(terms)
		elif bo == query.OPERATOR_OR:
			retrieved = self.union(terms)
		elif bo == query.OPERATOR_NOT:
			retrieved = self.complement(terms)
		
		return retrieved
	
	def intersect(self, terms):
		if not terms:
			return set()
		out = set(self.documents)

		for t in terms:
			if t in self.vocabulary.content:
				termId = self.vocabulary.getId(t)
				out &= set(self.postings.getDocsIdFromTerm(termId))
			else:
				return set()

		return out

	def union(self, terms):
		out = set()
		for t in terms:
			if t in self.vocabulary.content:
				termId = self.vocabulary.getId(t)
				out |= set(self.postings.getDocsIdFromTerm(termId))
		return out


	def complement(self, terms):
		if not terms:
			return set()

		out = set(self.documents)
		for t in terms:
			unwanted = set()
			if t in self.vocabulary.content:
				termId = self.vocabulary.getId(t)
				unwanted = set(self.postings.getDocsIdFromTerm(termId))
			out -= unwanted

		return out

	def positionalRetrieve(self, query):
		terms = query.setOfWords
		po = query.positionalOperator

		if po == query.OPERATOR_ADJACENT:
			retrieved = self.retrieveAtDistance(terms, 1)
		elif po == query.OPERATOR_CLOSE:
			retrieved = self.retrieveAtDistance(terms, 5)
		# SI ES un numero, busco por cercania N
		elif po >= 0:
			retrieved = self.retrieveAtDistance(terms, po)

		return retrieved
	
	def retrieveAtDistance(self, terms, distance):

		# Recibe dos listas con posiciones
		# Devuelve True si hay una posicion a la distancia dada
		def isPositionAtDistance(list1, list2, distance):
			if not isinstance(list1,list): list1 = [list1]
			if not isinstance(list2,list): list2 = [list2]
			for i in list1: 
				for j in list2:
					if abs(i - j) <= distance: return True
			return False

		retrieved = set()
		if len(terms) >= 2:
			t1 = list(terms)[0]
			t2 = list(terms)[1]
			if t1 in self.vocabulary.content and t2 in self.vocabulary.content:
				sharedDocs = self.intersect([t1,t2])
				if sharedDocs:
					termId1 = self.vocabulary.getId(t1)
					termId2 = self.vocabulary.getId(t2)
					pT1 = self.postings.getPosting(termId1)
					pT2 = self.postings.getPosting(termId2)
					for doc in sharedDocs:
						if doc in pT1 and doc in pT2 and isPositionAtDistance(pT1[doc], pT2[doc], distance):
							retrieved.add(doc)

		return retrieved

class VectorRetriever(object):

	WEIGHT_TF_IDF = "tf_idf"
	RANK_SCALAR_PRODUCT = "scalar_product"
	RANK_COSINE_SIMILARITY= "cosine_similarity"
	RANK_JACCARD = "jaccard"
	RANK_DICE = "dice"

	def __init__(self, vocabulary, postings, documents, documentsTerms):
		self.vocabulary = vocabulary
		self.postings = postings
		self.documents = documents.content
		self.documentsTerms = documentsTerms
		self.documentsNorm = {}

		# Weight: TF_IDF POR DEFECTO
		self.setWeights(self.WEIGHT_TF_IDF)

		# Rank: DICE por defecto
		self.setRank(self.RANK_COSINE_SIMILARITY)

	def setWeights(self, weight):
		self.weight = weight
		if weight == self.WEIGHT_TF_IDF:
			self.calculateTfIdf()

	def setRank(self, rank):
		self.rank = rank
		if rank == self.RANK_COSINE_SIMILARITY or rank == self.RANK_JACCARD or rank == self.RANK_DICE:
			self.setDocumentsNorm()

	def setDocumentsNorm(self):
		for d in self.documentsTerms:
			total = 0.0
			for t in self.documentsTerms[d]:
				p = self.postings.getPosting(t)
				total += p[d] ** 2.0
			self.documentsNorm[d] = total ** 0.5

	def getQueriesNorm(self, queries):
		qNorm = {}
		for q in queries:
			qNorm[q] = 0.0 
			for t in queries[q]:
				qNorm[q] += queries[q][t] ** 2
			qNorm[q] = qNorm[q] ** 0.5
		return qNorm

	def calculateTfIdf(self):
		# Seteo idf
		if not self.vocabulary.hasIdf():
			self.vocabulary.setIdf(len(self.documents))

		# Maximas frecuencias de cada documento
		maxTfreq = {}
		for d in self.documentsTerms:
			maxTfreq[d] = 0
			for t in self.documentsTerms[d]:
				tfreq = self.postings.getValue(t, d)
				if tfreq > maxTfreq[d]: maxTfreq[d] = tfreq

		# Seteo TF_idf como valor de la posting
		for t in self.vocabulary.content:
			termId = self.vocabulary.getId(t)
			p = self.postings.getPosting(termId)
			[self.postings.addDocToPosting(termId, docId, (p[docId] / maxTfreq[docId]) * self.vocabulary.getIdf(t)) for docId in p]

	def getRank(self, queries):
		if self.weight == self.WEIGHT_TF_IDF:
			queries = self.getQueriesWeight(queries)
		
		scalarProductRank = self.getScalarProductRank(queries)
		if self.rank == self.RANK_SCALAR_PRODUCT:
			return scalarProductRank
		qNorm = self.getQueriesNorm(queries)
		if self.rank == self.RANK_COSINE_SIMILARITY:
			return self.getCosineSimilarityRank(scalarProductRank, self.documentsNorm, qNorm)
		if self.rank == self.RANK_JACCARD:
			return self.getJaccardRank(scalarProductRank, self.documentsNorm, qNorm)
		if self.rank == self.RANK_DICE:
			return self.getDiceRank(scalarProductRank, self.documentsNorm, qNorm)

	def getQueriesWeight(self, queries):
		queriesWeight = {}
		for q in queries:
			queriesWeight[q.num] = {}
			for t in q.bagOfWords:
				if t in self.vocabulary.content:
					queriesWeight[q.num][t] = q.bagOfWords[t] * self.vocabulary.getIdf(t) 
		return queriesWeight

	def getScalarProductRank(self, queries):
		scalarProduct = {}
		for q in queries:
			scalarProduct[q] = {}
			for d in self.documentsTerms:
				sp = 0.0
				for t in queries[q]:
					termId = self.vocabulary.getId(t)
					if termId in self.documentsTerms[d]:
						sp += self.postings.getPosting(termId)[d] * queries[q][t]
				if sp > 0.0:
					scalarProduct[q][d] = sp
		return scalarProduct

	def getCosineSimilarityRank(self, scalarProductRank, documentsNorm, queriesNorm):
		cosineSimilarity = {}
		for q in scalarProductRank:
			cosineSimilarity[q] = {}
			for d in scalarProductRank[q]:
				if (documentsNorm[d] * queriesNorm[q]) != 0.0:
					cosineSimilarity[q][d] = scalarProductRank[q][d] / (documentsNorm[d] * queriesNorm[q])
		return cosineSimilarity

	def getJaccardRank(self, scalarProductRank, documentsNorm, queriesNorm):
		jaccardRank = {}
		for q in scalarProductRank:
			jaccardRank[q] = {}
			for d in scalarProductRank[q]:
				divider = (documentsNorm[d] ** 2.0) + (queriesNorm[q] ** 2.0) - scalarProductRank[q][d]
				if divider != 0.0:
					jaccardRank[q][d] = scalarProductRank[q][d] / divider
		return jaccardRank

	def getDiceRank(self, scalarProductRank, documentsNorm, queriesNorm):
		diceRank = {}
		for q in scalarProductRank:
			diceRank[q] = {}
			for d in scalarProductRank[q]:
				divider = (documentsNorm[d] ** 2.0) + (queriesNorm[q] ** 2.0)
				if divider != 0:
					diceRank[q][d] = (2.0 * scalarProductRank[q][d]) / divider
		return diceRank

	def printRankingFile(self, ranksByQuery, title):	
		with open(title+".res", "w") as f:		
			s = []
			for qId in ranksByQuery:
				rank = 0
				for docId in sorted(ranksByQuery[qId], key=lambda x: (ranksByQuery[qId][x]), reverse=True):
					s.append("%d %s %d %d %f %s\n" 
						% (qId,
							"Q0",
							docId, 
							rank,
							ranksByQuery[qId][docId],
							"JCAR_2016"))
					rank += 1
			f.write(''.join(s))
		return title