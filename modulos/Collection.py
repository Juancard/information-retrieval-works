# -*- coding: utf-8 -*-

import os

class Collection(object):

	def __init__(self, path):
		self.content = False
		self.path = path
		if not os.path.isdir(path):
			raise OSError(u'La coleccion dada no es un directorio valido')
		try:
			self.content = os.listdir(path)
		except:
			raise OSError(u'La coleccion dada no es un directorio existente')

	def onlyFiles(self):
		"""Devuelve solo los archivos de la coleccion"""
		return [f for f in self.content if os.path.isfile(os.path.join(self.path, f))]

	def filesAndDirectories(self):
		"""Devuelve archivos y subdirectorios de la coleccion"""
		return self.content
	
	def allFiles(self):
		"""Devuelve todos los archivos incluyendo archivos en todos los subdirectorios"""
		allFiles = []		
		for dirpath, dirnames, filenames in os.walk(self.path):
			for filename in filenames:
        			allFiles.append(os.path.join(dirpath, filename))
		return allFiles

	def getName(self):
		return os.path.basename(os.path.normpath(self.path))
