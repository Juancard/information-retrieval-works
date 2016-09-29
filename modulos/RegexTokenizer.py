import re
import unicodedata

class Replacement(object):

    def __init__(self, replacement):
        self.replacement = replacement
        self.occurrences = []

    def __call__(self, match):
        matched = match.group(0)
        replaced = match.expand(self.replacement)
        self.occurrences.append((matched, replaced))
        return replaced

class RegexTokenizer(object):
	
	def __init__(self):
		self.htmlChars = []
		self.abreviaturas = []
		self.numeros = []
		self.urls = []
		self.mails = []
		self.nombresPropios = []

	def getMatched(self,pattern,repl,line):
		match = {
			"final_string": "",
			"tokens_matched": []
		}
		repl = Replacement(repl)
		match["final_string"] = re.sub(pattern, repl, line)
		for matched, replaced in repl.occurrences:
			match["tokens_matched"].append(matched)
		return match

	def extraerAbreviaturas(self,linea):
		
		#NO suficientemente testeadas
		##abrev4 = r"([A-Za-z][A-Za-z]*\.)([,?]| [a-z0-9])"
		##de paper, no funcionando: 
		###([A-Za-z][^ ]*\.)([,?]| [a-z0-9])
		##abrev1 = r"\s([A-Za-z]\.)\s" 

		abrev2 = r"([A-Za-z]\.(?:[A-Za-z0-9]\.)+)"
		abrev3 = r"[A-Z][bcdfghj-np-tvxz]+\."
		
		matched = self.getMatched(abrev3+r"|"+abrev2,"",linea)
		self.abreviaturas.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def extraerHtmlChars(self,linea):

		#Special HTML characters
		amp = r"\s(&[\S^;]+;)"
		amp2 = r"&(?:[a-z]+|#x?\d+);"

		matched = self.getMatched(amp2,"",linea)
		self.htmlChars.extend(matched["tokens_matched"])
		matched = self.getMatched(amp,"",matched["final_string"])
		self.htmlChars.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def extraerNumeros(self,linea):

		date = r"[0-9]{1,2}[\/|\-][0-9]{1,2}[\/|\-](?:[0-9]{2,4})"
		porcentaje = r"(\+\-)?[0-9]+(.)?[0-9]*%"
		moneda = r"\$\d+(?:,\d{1,2})?"
		
		# Demasiados falsos positivos:
		# telefono = r"(?<=\s|:)\(?(?:(0?[1-3]\d{1,2})\)?(?:\s|-)?)?((?:\d[\d-]{5}|15[\s\d-]{7})\d+)"
		
		# Solo acepta telefonos comenzados con codigo de area entre parentesis
		telefono2 = r"(?:\(\d{2,}\))\s?\d{2,}(?:\-\d+)?\s"
		
		matched = self.getMatched(date,"",linea)
		self.numeros.extend(matched["tokens_matched"])
		matched = self.getMatched(porcentaje,"",matched["final_string"])
		self.numeros.extend(matched["tokens_matched"])
		matched = self.getMatched(moneda,"",matched["final_string"])
		self.numeros.extend(matched["tokens_matched"])
		matched = self.getMatched(telefono2,"",matched["final_string"])
		self.numeros.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def extraerUrls(self,linea):
		pattern = r"(https?:\/\/(?:www\.|(?!www))[a-z0-9\.]+\.[a-z0-9\/\?=]{2,}|www\.[a-z0-9]+\.[a-z0-9\/\?=]{2,})"
		
		matched = self.getMatched(pattern,"",linea)
		self.urls.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def extraerMails(self,linea):
		pattern = r"[a-zA-Z0-9!#\$%&'\*\+\-\/=\?\^_`{\|}~\.]+@[a-z0-9\-]+\.[a-z]+(?:\.[a-z]+)+"
		
		matched = self.getMatched(pattern,"",linea)
		self.mails.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def extraerNombresPropios(self,linea):
		# Elimino acentos
		nfkd_form = unicodedata.normalize('NFKD', linea)
		linea = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
		
		pattern=r"[A-Z][a-z]+(?:[\s][A-Z][a-z]+)+"
		
		matched = self.getMatched(pattern,"",linea)
		self.nombresPropios.extend(matched["tokens_matched"])
		
		return matched["final_string"]

	def getAllTokens(self):
		out = self.nombresPropios + self.mails + self.htmlChars + self.abreviaturas + self.numeros + self.urls
		return out

