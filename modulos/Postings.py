from abc import ABCMeta, abstractmethod
import codecs
import collections

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
		self.content[term] = {
			docId: value
		}

	def addDocToPosting(self, term, docId, value):
		if term in self.content:
			self.content[term][docId] = value

	def isPosting(self, term):
		return term in self.content

	def getValue(self, term, docId):
		return self.getPosting(term)[docId]

	def sortByKey(self):
		ordered = collections.OrderedDict()
		for key, values in sorted(self.content.items()):
			ordered[key] = values
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
						docStr += "%s%d" % (self.SEPARATOR_VALUE, value)
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
		posting = {}
		for doc in strPosting.split(self.SEPARATOR_DOC):
			values = doc.split(self.SEPARATOR_VALUE)
			if len(values) == 2:
				posting[int(values[0])] = int(values[1])
			elif len(values) > 2:
				posting[int(values[0])] = [int(i) for i in values[1:]]
		return posting

	def getDocsIdFromTerm(self, term):
		p = self.getPosting(term)
		return p.keys()
