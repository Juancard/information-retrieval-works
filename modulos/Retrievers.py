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

	def __init__(self, vocabulary, postings, documentsTerms, 
		weight=WEIGHT_TF_IDF, rank=RANK_SCALAR_PRODUCT,
		documentsNorm={}):
		self.vocabulary = vocabulary
		self.postings = postings
		self.documentsTerms = documentsTerms
		self.documentsNorm = documentsNorm

		# Weight: TF_IDF POR DEFECTO
		self.weight = weight

		# Rank por defecto
		self.rank = rank

	def getQueryNorm(self, query):
		qNorm = 0.0 
		for t in query:
			qNorm += query[t] ** 2
		qNorm = qNorm ** 0.5
		return qNorm


	def getRank(self, queries):
		if self.weight == self.WEIGHT_TF_IDF:
			queries = self.getQueriesWeight(queries)

		rank = {}

		for q in queries:
			print "Procesando query %s" % q
			rank[q] = self.getScalarProductRank(queries[q])
			if not self.rank == self.RANK_SCALAR_PRODUCT:
				qNorm = self.getQueryNorm(queries[q])
				if self.rank == self.RANK_COSINE_SIMILARITY:
					rank[q] = self.getCosineSimilarityRank(rank[q], qNorm)
				if self.rank == self.RANK_JACCARD:
					rank[q] = self.getJaccardRank(rank[q], qNorm)
				if self.rank == self.RANK_DICE:
					rank[q] = self.getDiceRank(rank[q], qNorm)
		return rank

	def getQueriesWeight(self, queries):
		queriesWeight = {}
		for q in queries:
			queriesWeight[q.num] = {}
			for t in q.bagOfWords:
				if t in self.vocabulary.content:
					queriesWeight[q.num][t] = q.bagOfWords[t] * self.vocabulary.getIdf(t) 
		return queriesWeight

	def getScalarProductRank(self, query):
		scalarProduct = {}
		for d in self.documentsTerms:
			sp = 0.0
			for t in query:
				termId = self.vocabulary.getId(t)
				if termId in self.documentsTerms[d]:
					sp += self.postings.getPosting(termId)[d] * query[t]
			if sp > 0.0:
				scalarProduct[d] = sp
		return scalarProduct

	def getCosineSimilarityRank(self, scalarProductRank, qNorm):
		cosineSimilarity = {}
		for d in scalarProductRank:
			if (self.documentsNorm[d] * qNorm) != 0.0:
				cosineSimilarity[d] = scalarProductRank[d] / (self.documentsNorm[d] * qNorm)
		return cosineSimilarity

	def getJaccardRank(self, scalarProductRank, qNorm):
		jaccardRank = {}
		for d in scalarProductRank:
			divider = (self.documentsNorm[d] ** 2.0) + (qNorm ** 2.0) - scalarProductRank[d]
			if divider != 0.0:
				jaccardRank[d] = scalarProductRank[d] / divider
		return jaccardRank

	def getDiceRank(self, scalarProductRank, qNorm):
		diceRank = {}
		for d in scalarProductRank:
			divider = (self.documentsNorm[d] ** 2.0) + (qNorm ** 2.0)
			if divider != 0:
				diceRank[d] = (2.0 * scalarProductRank[d]) / divider
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
							self.rank))
					rank += 1
			f.write(''.join(s))
		return title