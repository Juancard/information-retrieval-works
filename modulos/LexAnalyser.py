# -*- coding: utf-8 -*-

import os
import sys
import codecs
import unicodedata
import string
import re
from nltk.stem.snowball import SnowballStemmer

# Mi modulo para extraer expresiones regulares
from RegexTokenizer import RegexTokenizer

class LexAnalyser(object):

	def __init__(self, config):
		self.config = False
		self.stopwords = False
		self.regex = False
		self.stem = False
		self.termMaxSize = sys.maxint
		self.termMinSize = -1
		self.configure(config)

	def configure(self, config):
		if "stopwords" in config and config["stopwords"]:
			self.stopwords = self.getStopwordsFromPath(config["stopwords"])
		if "stem" in config:
			self.stem = config["stem"]
		if "regex" in config:
			self.regex = config["regex"]
		if "term_min_size" in config:
			self.termMinSize = int(config["term_min_size"])			
		if "term_max_size" in config:
			self.termMaxSize = int(config["term_max_size"])

	def analyse(self, line):

		# Antes de tokenizar, aplico regex
		regexTokens = []
		regexTerms = []
		if self.regex:
			extraido = self.getRegexTokens(line)
			regexTokens.extend(extraido["tokens"])
			regexTerms.extend(extraido["terms"])
			line = extraido["final_string"]

		# Normalizo y tokenizo
		tokens = self.tokenize(line)
		terms = tokens

		# Quito palabras vacias
		if self.stopwords:
			terms = [t for t in terms if t not in self.stopwords]

		if self.stem:
			terms = self.doStem(terms, self.stem)
				
		terms = [t for t in terms if self.isValidTermLength(t)]

		# Uno con resultados de regex
		tokens.extend(regexTokens)
		terms.extend(regexTerms)

		return {
			"tokens": tokens,
			"terms": terms
		}

	def getStopwordsFromPath(self, path):
		out = []

		if not os.path.isfile(path):
			return False
		
		with codecs.open(path, mode='rt', encoding='utf-8') as f:
			for line in f:
				out.extend(self.tokenize(line))

		return out

	def tokenize(self, toTokenize):
		# Normalizo
		toTokenize = toTokenize.rstrip() # equivalente a chomp de perl
		toTokenize = self.removeAccents(toTokenize) # quito acentos
		toTokenize = toTokenize.lower() # mayusculas a minusculas
		toTokenize = self.removePuntuaction(toTokenize) # remuevo simbolos de puntuacion
		toTokenize = self.removeCharacters(toTokenize) # quito otros caracteres
		lista_tokens = toTokenize.split() # separo por espacio
		return lista_tokens

	def removeAccents(self, inputString):
		nfkd_form = unicodedata.normalize('NFKD', inputString)
		out = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
		return out

	def removePuntuaction(self, inputString):
		punctuation = u"¿¡" + string.punctuation
		return self.regexRemove(punctuation, inputString)

	def removeCharacters(self, inputString):
		characters = u"§âÂ¢«»­±¬ºï©®Ÿ€¾°“”·—’‘–Ã¼ü"
		return self.regexRemove(characters, inputString)

	def regexRemove(self, toRemove, inputString):
		regex = re.compile('[%s]' % re.escape(toRemove))
		return regex.sub('',inputString)

	def isValidTermLength(self, token): 
		return len(token) >= self.termMinSize and len(token) <= self.termMaxSize
	
	def doStem(self, tokens, language):
		out = []
		stemmer = SnowballStemmer(language)
		for token in tokens:
			out.append(stemmer.stem(token))
		return out

	# Recibe un string y devuelve los tokens extraidos
	# y un subconjunto de esos tokens que son los terminos 
	def getRegexTokens(self, linea):
		# Lo que devuelve la funcion
		out = {
			"tokens": [],
			"terms": [],
			"final_string": ""
		}
		regexTokenizer = RegexTokenizer()

		# Extraigo los tokens que matchea con esa linea
		linea = regexTokenizer.extraerAbreviaturas(linea)
		linea = regexTokenizer.extraerHtmlChars(linea)
		linea = regexTokenizer.extraerNumeros(linea)
		linea = regexTokenizer.extraerUrls(linea)
		linea = regexTokenizer.extraerMails(linea)
		linea = regexTokenizer.extraerNombresPropios(linea)	
		
		# Todos los tokens que extrajo
		out["tokens"] = regexTokenizer.getAllTokens()
		out["final_string"] = linea

		# Los tokens que no deseo guardar en indice
		# En este caso solo deshecho los chars html
		tokensPorQuitar = regexTokenizer.htmlChars

		# Cargo los terminos
		for token in out["tokens"]:
			if token not in tokensPorQuitar:
				out["terms"].append(token)

		return out