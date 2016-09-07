# -*- coding: utf-8 -*-
import numpy as np
import collections

class Vocabulary(object):

	def __init__(self):
		self.content = {}

	def addTerm(self, term, cf, df):
		self.content[term] = {
			"cf": cf,
			"df": df
		}

	def incrementCF(self, term, n):
		if self.isATerm(term):
			self.content[term]["cf"] += n

	def incrementDF(self, term, n):
		if self.isATerm(term):
			self.content[term]["df"] += n

	def getCF(self, term):
		out = 0
		if self.isATerm(term):
			out = self.content[term]["cf"]
		return out

	def getDF(self, term):
		out = 0
		if self.isATerm(term):
			out = self.content[term]["df"]
		return out

	def setIdf(self, DocsLength):
		try:
			for t in self.content:
				self.content[t]["idf"] = np.log(DocsLength / self.content[t]["df"])
		except KeyError:
			return False

	def getIdf(self, term):
		return self.content[term]["idf"]

	def hasIdf(self):
		return "idf" in self.content

	def isATerm(self, term):
		return term in self.content

	def setId(self, term, termId):
		try:
			self.content[term]["id"] = termId
			return True
		except KeyError:
			return False

	def getId(self, term):
		return self.content[term]["id"]

	def orderByFrecuenceValue(self, isDesc):
		return sorted(self.content, key=lambda x: (self.content[x]['cf'], self.content[x]['df']), reverse=isDesc)

	def setAlphabeticalOrder(self):
		ordered = collections.OrderedDict()
		for key, values in sorted(self.content.items()):
			ordered[key] = values
		self.content = ordered

	def printTopKFile(self, title, k):
		with open(title, "w") as topKFile:
			s = []
			s.append("-"*50+"\n")
			s.append("\tRANKING \tpor Juan Cardona\n")
			s.append("-"*50+"\n")
		
			s.append("LOS %d TÉRMINOS MÁS FRECUENTES\n" % k)
			s.append("\n\tTERMINO - CF\n")

			maxCFList = self.orderByFrecuenceValue(True)[0:k]
			for term in maxCFList:
				s.append("\t%s - %d\n" % (term.encode('UTF-8'), self.getCF(term)))
			
			minCFList = self.orderByFrecuenceValue(False)[0:k]
			s.append("\nLOS %d TÉRMINOS MENOS FRECUENTES\n" % k)
			s.append("\n\tTERMINO - CF\n")
			for term in minCFList:
				s.append("\t%s - %d\n" % (term.encode("UTF-8"), self.getCF(term)))
			
			topKFile.write(''.join(s))
		return title

	def printTermsFile(self, title):
		with open(title, "w") as f:
			f.write("-"*50+"\n")
			f.write("\tTERMINOS \tpor Juan Cardona\n")
			f.write("-"*50+"\n")
			f.write("TERMINO - FRECUENCIA - DF:\n")
			for k in self.orderByFrecuenceValue(True):
				f.write("%s - %d - %d\n" % (k.encode('UTF-8'), self.getCF(k), self.getDF(k)))
		return title