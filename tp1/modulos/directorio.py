import sys
import os

class Directorio(object):

	def __init__(self, path):
		self.path = path
	
	def onlyFiles(self):
		"""Devuelve solo los archivos del directorio"""
		return [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]

	def filesAndDirectories(self):
		"""Devuelve archivos y subdirectorios del directorio dado"""
		return os.listdir(self.path)