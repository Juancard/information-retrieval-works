# -*- coding: utf-8 -*-

class Documents(object):

	def __init__(self):
		self.content = {}

	def addDocument(self, docId, name):
		if self.isDocument:
			self.content[docId] = name

	def isDocument(self, docId):
		return docId in self.content

	# Mapping de documento con id asignado
	def idToDocFile(self, title):
		with open(title+".txt", "w") as f:
			s = []
			for docId in self.content:
				s.append("%d %s\n" % (docId,self.content[docId]))
			f.write("".join(s))
		return title

