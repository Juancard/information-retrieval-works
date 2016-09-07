# -*- coding: utf-8 -*-
import pickle

class PicklePersist(object):

	def save(self, obj, name):
		title = name + '.pkl'
		with open(title, 'wb') as f:
			pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
		return title

	def load(self, name):
		try:
			with open(name + '.pkl', 'rb') as f:
				return pickle.load(f)
		except IOError:
			raise "Error al cargar archivo: %s" % name
