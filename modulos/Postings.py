from abc import ABCMeta, abstractmethod
import codecs
import collections
import struct
import sys
import numpy as np

class Postings(object):
	
	__metaclass__ = ABCMeta

	def __init__(self, content):
		self.content = content	

	@abstractmethod
	def getAll(self):
		""""Devuelve todas las postings"""
		pass

	@abstractmethod
	def getPosting(self, term):
		""""Devuelve la posting del termino"""
        pass    

	@abstractmethod
	def addPosting(self, term, docId, value):
		""""Agrega posting"""
        pass   

	@abstractmethod
	def addDocToPosting(self, term, docId, value):
		""""Agrega documento a la posting"""
        pass   
        
	@abstractmethod
	def isPosting(self, term):
		""""Devuelve verdadero si existe la posting para el termino dado"""
        pass   

	@abstractmethod
	def getValue(self, term, docId):
		""""Devuelve valor de la posting en el documento dado"""
        pass  

	def isDocInPosting(self, term, docId):
		return self.isPosting(term) and docId in self.getPosting(term)

class DictionaryPostings(Postings):

	def getAll(self):
		return self.content

	def getPosting(self, term):
		return self.content[term]

	def addPosting(self, term, docId, value):
		if term not in self.content:
			self.content[term] = {
				docId: value
			}
		else:
			self.addDocToPosting(term, docId, value)

	def addDocToPosting(self, term, docId, value):
		if term in self.content:
			self.content[term][docId] = value

	def isPosting(self, term):
		return term in self.content

	def getValue(self, term, docId):
		return self.getPosting(term)[docId]

	def sortByKey(self):
		ordered = collections.OrderedDict()
		for t, tValues in sorted(self.content.items()):
			tValuesOrdered = collections.OrderedDict()
			for d, dValues in sorted(tValues.items()):
				tValuesOrdered[d] = dValues
			ordered[t] = tValuesOrdered
		self.content = ordered

	def termToId(self, term, termId):
		try:
			allPostings = self.getAll()
			aux = allPostings[term]
			del allPostings[term]
			allPostings[termId] = aux
			return True
		except KeyError:
			return False

	def getStats(self):
		allPostings = self.getAll()
		stats = {}
	
		if allPostings:
			# Inicializo valores
			stats["min_len_posting"] = sys.maxint
			stats["max_len_posting"] = 0
			stats["sum_len_posting"] = 0.0
	
			for p in allPostings:
				lenP = len(allPostings[p])
				if lenP > stats["max_len_posting"]:
					stats["max_len_posting"] = lenP
				if lenP < stats["min_len_posting"]:
					stats["min_len_posting"] = lenP
				stats["sum_len_posting"] += lenP
	
			stats["mean_len_posting"] = stats["sum_len_posting"] / len(allPostings)

		return stats

class SequentialPostings(Postings):

	SEPARATOR_TERM = ":"
	SEPARATOR_DOC = ";"
	SEPARATOR_VALUE = ","

	def __init__(self, path):
		self.path = path

	@classmethod
	def create(self, postings, path=None, title=None):
		if path is None:
			path = "index_data/"
		if title is None:
			title = "seq_postings.txt"
		with open(path + title, "w") as f:
			allStr = []
			for t in postings:
				postingStr = ["%d%s" % (t, self.SEPARATOR_TERM)]
				for d in postings[t]:
					value = postings[t][d]
					docStr = "%d" % d
					if isinstance(value, list):
						for item in value:
							docStr += "%s%d" % (self.SEPARATOR_VALUE, item)
					else:
						docStr += "%s%.6f" % (self.SEPARATOR_VALUE, value)
					docStr += "%s" % (self.SEPARATOR_DOC)
					postingStr.append(docStr)
				postingStr.append('\n')
				allStr.extend(postingStr)
			f.write(''.join(allStr))
		return SequentialPostings(path+title)

	def getAll(self):
		""""Devuelve todas las postings"""
		postings = collections.OrderedDict()
		with codecs.open(self.path, mode='rt', encoding='utf-8') as f:
			for line in f:
				line = line.rstrip().split(self.SEPARATOR_TERM)
				postings[int(line[0])] = self.makePostingFromString(line[1])
		return postings

	def getPosting(self, term):
		""""Devuelve la posting del termino"""
		with codecs.open(self.path, mode='rt', encoding='utf-8') as f:
			for line in f:
				splitted = line.split(self.SEPARATOR_TERM)
				if int(splitted[0]) == term:
					return self.makePostingFromString(splitted[1])
		return False

	def addPosting(self, term, docId, value):
		""""Agrega posting"""
        pass   

	def addDocToPosting(self, term, docId, value):
		""""Agrega documento a la posting"""
        pass   
        
	def isPosting(self, term):
		with codecs.open(self.path, mode='rt', encoding='utf-8') as f:
			for line in f:
				splitted = line.split(self.SEPARATOR_TERM)
				if int(splitted[0]) == term:  
					return True
		return False

	def getValue(self, term, docId):
		""""Devuelve valor de la posting en el documento dado"""
		posting = self.getPosting(term)
		if posting and docId in posting:
			return posting[docId]
		else:
			return False

	def makePostingFromString(self, strPosting):
		posting = collections.OrderedDict()
		for doc in strPosting.split(self.SEPARATOR_DOC):
			values = doc.split(self.SEPARATOR_VALUE)
			if len(values) == 2:
				posting[int(values[0])] = float(values[1])
			elif len(values) > 2:
				posting[int(values[0])] = [int(i) for i in values[1:]]
		return posting

	def getDocsIdFromTerm(self, term):
		return self.getPosting(term).keys()
		

class BinaryPostings(object):
	
	def __init__(self, path, termToPointer, dgaps=False):
		self.path = path
		self.termToPointer = termToPointer
		self.skipLists = {}
		self.dgaps = False

	@classmethod
	# CUIDADO: DGAPS AUN NO COMPLETO, NO IMPLEMENTAR
	def create(self, postings, path="index_data/", 
			title="binary_postings.dat", dgaps=False):
		path = path + title
		termToPointer = collections.OrderedDict()
		pointer = 0
		with open(path, "wb") as f:
			for pId in postings:
				termToPointer[pId] = {
					"pointer": pointer,
					"lenDocs": len(postings[pId])
				}
				docIds = postings[pId].keys()
				if dgaps:
					docsToWrite = self.deltaEncode(self, docIds)
				else:
					docsToWrite = docIds
				f.write(struct.pack('<%sI' % len(docsToWrite), *docsToWrite))
				for docId in docIds:
					f.write(struct.pack('<f', postings[pId][docId]))
				pointer += len(docIds) * 4 * 2
		return BinaryPostings(path, termToPointer, dgaps)

	@staticmethod
	# NO IMPLEMENTAR
	def deltaEncode(self, docsId):
		out = [docsId[0]]
		for i in range(1, len(docsId)):
			out.append(docsId[i] - docsId[i-1])
		return out

	def getAll(self):
		postings = collections.OrderedDict()
		for term in self.termToPointer:
			postings[term] = self.getPosting(term)
		return postings

	def getPosting(self, term):
		posting = collections.OrderedDict()
		with open(self.path, "rb") as f:

			# Me posiciono en el termino
			f.seek(self.termToPointer[term]["pointer"])

			# Leo longitud de documents Id
			lenDocs = self.termToPointer[term]["lenDocs"]

			# Leo documents ids
			bDocs = f.read(lenDocs * 4)
			docIds = struct.unpack('<%iI' % lenDocs, bDocs)

			# Leo frecuencias
			bFreqs = f.read(lenDocs * 4)
			freqs = struct.unpack('<%if' % lenDocs, bFreqs)

			# Armo posting
			for i in range(len(docIds)):
				posting[docIds[i]] = freqs[i]

		return posting

	def addPosting(self, term, docId, value):
		""""Agrega posting"""
        pass   

	def addDocToPosting(self, term, docId, value):
		""""Agrega documento a la posting"""
        pass   
        
	def isPosting(self, term):
		""""Devuelve verdadero si existe la posting para el termino dado"""
        pass   

	def getValue(self, term, docId):
		""""Devuelve valor de la posting en el documento dado"""
        pass  

	def getDocsIdFromTerm(self, term):
		out = {}
		with open(self.path, "rb") as f:

			# Me posiciono en el termino
			f.seek(self.termToPointer[term]["pointer"])

			# Leo longitud de documents Id
			lenDocs = self.termToPointer[term]["lenDocs"]

			# Leo documents ids
			bDocs = f.read(lenDocs * 4)
			out = list(struct.unpack('<%iI' % lenDocs, bDocs))

		return out

	def createSkipLists(self):
		skipLists = {}
		with open(self.path, "rb") as f:
			for term in self.termToPointer:
				# Leo longitud de documents Id
				lenDocs = self.termToPointer[term]["lenDocs"]
				
				if lenDocs < 2:
					totalSkipPointers = lenDocs
				else:
					totalSkipPointers = int(np.sqrt(lenDocs)) + 1
				step = lenDocs / totalSkipPointers

				sl = collections.OrderedDict()
				pointer = self.termToPointer[term]["pointer"]
				for i in range(totalSkipPointers):
					pointer += (step - 1) * 4
					f.seek(pointer)
					bDoc = f.read(4)
					docId = struct.unpack('<I', bDoc)[0]
					sl[docId] = pointer
					pointer += 4

				skipLists[term] = sl

		return skipLists

	def setSkipLists(self, sl):
		self.skipLists = sl

	def intersect(self, t1, t2):
		out = set()
		p1 = self.termToPointer[t1]["pointer"]
		endP1 = p1 + (self.termToPointer[t1]["lenDocs"] * 4)
		p2 = self.termToPointer[t2]["pointer"]
		endP2 = p2 + (self.termToPointer[t2]["lenDocs"] * 4)
		with open(self.path, "rb") as f:
			while p1 < endP1:
				f.seek(p1)
				docT1 = struct.unpack("<I", f.read(4))[0]
				while p2 < endP2:
					f.seek(p2)
					docT2 = struct.unpack("<I", f.read(4))[0]
					if docT2 == docT1:
						out.add(docT1)
					p2 += 4
				p1 += 4
		return out

	def intersectWithSkip(self, t1, t2):
		out = set()

		p1 = self.termToPointer[t1]["pointer"]
		endP1 = p1 + (self.termToPointer[t1]["lenDocs"] * 4)
		p2 = self.termToPointer[t2]["pointer"]
		endP2 = p2 + (self.termToPointer[t2]["lenDocs"] * 4)
		with open(self.path, "rb") as f:
			while p1 < endP1 and p2 < endP2:
				f.seek(p1)
				docT1 = struct.unpack("<I", f.read(4))[0]
				f.seek(p2)
				docT2 = struct.unpack("<I", f.read(4))[0]
				if docT1 == docT2:
					out.add(docT1)
					p1 += 4; p2 += 4
				elif docT1 < docT2:
					p1HasChanged = False
					for skipDoc in self.skipLists[t1]:
						if skipDoc <= docT2:
							if skipDoc > docT1:
								p1 = self.skipLists[t1][skipDoc]
								p1HasChanged = True
						else: break
					if not p1HasChanged: p1 += 4
				else:
					p2HasChanged = False
					for skipDoc in self.skipLists[t2]:
						if skipDoc <= docT1:
							if skipDoc > docT2:
								p2 = self.skipLists[t2][skipDoc]
								p2HasChanged = True
						else: break
					if not p2HasChanged: p2 += 4
		return out