# -*- coding: utf-8 -*-
import collections

class BooleanRetriever(object):
	"""Realiza recuperaciones en base al modelo booleano"""
	def __init__(self, vocabulary, postings, documents, skipLists=False):
		self.vocabulary = vocabulary
		self.postings = postings
		self.documents = documents
		self.skipLists = skipLists

	def retrieve(self, queries):
		retrieved = {}
		for q in queries:
			print "Procesando query %s" % q.num
			if q.positionalOperator:
				retrieved[q.num] = self.positionalRetrieve(q)
			elif q.booleanOperator:
				retrieved[q.num] = self.booleanRetrieve(q)
			elif q.phraseOperator:
				retrieved[q.num] = self.phraseRetrieve(q)
			else:
				retrieved[q.num] = self.union(q.getSetOfWords())
		return retrieved

	def booleanRetrieve(self, query):
		terms = query.getSetOfWords()
		bo = query.booleanOperator

		if bo == query.OPERATOR_AND:
			retrieved = self.intersect(terms)
		elif bo == query.OPERATOR_OR:
			retrieved = self.union(terms)
		elif bo == query.OPERATOR_NOT:
			retrieved = self.complement(terms)
		
		return retrieved
	
	def intersect(self, terms):
		# SI NO HAY TERMINOS DEVUELVO CONJUNTO VACIO
		if not terms: return set()

		#Si alguno de los terminos no se encuentra en el vocabulario
		# se devuelve conjunto vacio
		for t in terms:
			if t not in self.vocabulary.content: return set()

		if self.skipLists:
			if len(terms) > 1:
				t1 = self.vocabulary.getId(list(terms)[0])
				t2 = self.vocabulary.getId(list(terms)[1])
				return self.postings.intersectWithSkip(t1, t2)
		
		# Si hay funcion intersect la llamo, caso contrario ejecuto la propia
		try:
			t1 = self.vocabulary.getId(list(terms)[0])
			t2 = self.vocabulary.getId(list(terms)[1])
			return self.postings.intersect(t1, t2)
		except AttributeError, KeyError:
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

	def phraseRetrieve(self, query):

		# HAY AL MENOS DOS TERMINOS?
		if len(query.terms) < 2: return self.union(query.terms)

		# TODOS LOS TERMINOS ESTAN EN EL VOCABULARIO?
		for t in query.terms:
			if t not in self.vocabulary.content: return {}
		
		# COMPARTEN AL MENOS UN DOCUMENTO?
		sharedDocs = self.intersect(query.terms)
		if not sharedDocs: return {}

		# comparo distancias
		previousTerm = self.postings.getPosting(self.vocabulary.getId(query.terms[0]))
		i = 1
		while i < len(query.terms) and sharedDocs:
			auxDocs = set()
			actualTerm = self.postings.getPosting(self.vocabulary.getId(query.terms[i]))
			for doc in sharedDocs:
				matchedPositions = set()
				prevPos = previousTerm[doc]
				actualPos = actualTerm[doc]
				if not isinstance(prevPos,list): prevPos = [prevPos]
				if not isinstance(actualPos,list): actualPos = [actualPos]
				for i in prevPos:
					for j in actualPos:
						if j - i == 1: matchedPositions.add(j)
				if matchedPositions:
					auxDocs.add(doc)
				actualTerm[doc] = matchedPositions
			sharedDocs = auxDocs
			previousTerm = actualTerm
			i += 1
		return sharedDocs

	def positionalRetrieve(self, query):
		terms = query.getSetOfWords()
		po = query.positionalOperator

		if po == query.OPERATOR_ADJACENT:
			retrieved = self.retrieveAtDistance(terms, 1)
		elif po == query.OPERATOR_CLOSE:
			retrieved = self.retrieveAtDistance(terms, 5)
		# SI ES un numero, busco por cercania N
		elif po >= 0:
			retrieved = self.retrieveAtDistance(terms, po)

		return retrieved
	

	# Recibe dos listas con posiciones
	# Devuelve True si hay una posicion a la distancia dada
	def isPositionAtDistance(self, list1, list2, distance, left=False, right=False):
		if not isinstance(list1,list): list1 = [list1]
		if not isinstance(list2,list): list2 = [list2]
		for i in list1: 
			for j in list2:
				if left==right:
					if abs(i - j) <= distance: return True
				elif left:
					if j - i <= distance: return True
				elif right:
					if i - j <= distance: return True
		return False

	def retrieveAtDistance(self, terms, distance):
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
						if doc in pT1 and doc in pT2 and self.isPositionAtDistance(pT1[doc], pT2[doc], distance):
							retrieved.add(doc)

		return retrieved

class VectorRetriever(object):

	WEIGHT_TF_IDF = "tf_idf"
	RANK_SCALAR_PRODUCT = "scalar_product"
	RANK_COSINE_SIMILARITY= "cosine_similarity"
	RANK_JACCARD = "jaccard"
	RANK_DICE = "dice"

	def __init__(self, vocabulary, postings, documents, 
		weight=WEIGHT_TF_IDF, rank=RANK_SCALAR_PRODUCT,
		documentsNorm={}):
		self.vocabulary = vocabulary
		self.postings = postings
		self.documents = documents
		self.documentsNorm = documentsNorm
		self.weight = weight
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
			qBow = q.getBagOfWords()
			for t in qBow:
				if t in self.vocabulary.content:
					queriesWeight[q.num][t] = qBow[t] * self.vocabulary.getIdf(t) 
		return queriesWeight

	def term_at_a_time(self, queries, topk):
		rank = {}
		if self.weight == self.WEIGHT_TF_IDF:
			queries = self.getQueriesWeight(queries)

		for q in queries:
			postings = {}

			# Inicializo valores a cero
			rank[q] = collections.defaultdict(int)

			# Guardo postings de cada término
			for t in queries[q]:
				termId = self.vocabulary.getId(t)
				postingsList = self.postings.getPosting(termId)
				for doc in postingsList:
					rank[q][doc] += postingsList[doc]

			# Ordeno por frecuencia y doc y devuelvo tuplas (doc, score)
			orderedList = sorted(rank[q].items(), key = lambda l:( l[1], l[0]), reverse=True)[0:topk]
			
			# Cargo resultado final del query
			rank[q] = collections.OrderedDict()
			for doc, score in orderedList:
				rank[q][doc] = score

		return rank

	def document_at_a_time(self, queries, topk):
		if self.weight == self.WEIGHT_TF_IDF:
			queries = self.getQueriesWeight(queries)

		rank = {}
		for q in queries:
			postings = {}
			rank[q] = {}
			# Guardo postings de cada término
			for t in queries[q]:
				termId = self.vocabulary.getId(t)
				postings[termId] = self.postings.getPosting(termId)
			
			# Score mínimo aceptable en ranking
			minScore = 0
			for d in self.documents:
				d_score = 0
				for post in postings:
					if d in postings[post]:
						d_score += postings[post][d]

				# Solo agrego doc si supera el minimo score
				if d_score > minScore:	
					rank[q][d] = d_score

					# Si hay mas de k documentos
					if len(rank[q]) > topk:
						
						# Elimino el documento de menor score (y de mayor docid en caso de empate)
						min_value = min(rank[q].values())
						max_key = max([k for k in rank[q] if rank[q][k] == min_value])
						rank[q].pop(max_key)
						
						# Establezco nuevo score minimo
						minScore = rank[q][min(rank[q], key=rank[q].get)]

			# Ordeno por frecuencia y doc y devuelvo tuplas (doc, score)
			orderedList =sorted(rank[q].items(), key = lambda l:( l[1], l[0]), reverse=True)[0:topk]
			
			# Cargo resultado final del query
			rank[q] = collections.OrderedDict()
			for doc, score in orderedList:
				rank[q][doc] = score

		return rank

	def getScalarProductRank(self, query):
		scores = {}

		for t in query:
			termId = self.vocabulary.getId(t)
			post = self.postings.getPosting(termId)
			for d in post:
				if d not in scores: scores[d] = 0.0 
				scores[d] += post[d] * query[t]

		return scores

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