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
			terms = q.setOfWords
			if q.booleanOperator == q.OPERATOR_AND:
				retrieved[q.num] = self.intersect(terms)
			elif q.booleanOperator == q.OPERATOR_OR:
				retrieved[q.num] = self.union(terms)
			elif q.booleanOperator == q.OPERATOR_NOT:
				retrieved[q.num] = self.complement(terms)
			else:
				retrieved[q.num] = self.union(terms)
		return retrieved

	def intersect(self, terms):
		pass

	def union(self, terms):
		pass

	def complement(self, terms):
		out = set()
		for t in terms:
			unwanted = []
			if t in self.vocabulary.content:
				termId = self.vocabulary.getId(t)
				unwanted = self.postings.getDocsIdFromTerm(termId)
			[out.add(d) for d in self.documents if d not in unwanted]
		return out

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

		# Seteo TF_idf como valor de la posting
		for t in self.vocabulary.content:
			termId = self.vocabulary.getId(t)
			p = self.postings.getPosting(termId)
			maxTfreq = max([p[docId] for docId in p])
			[self.postings.addDocToPosting(termId, docId, (p[docId] / maxTfreq) * self.vocabulary.getIdf(t)) for docId in p]

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