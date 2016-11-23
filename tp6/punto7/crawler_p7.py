# -*- coding: utf-8 -*-
import sys
import os
import json
import re
import urllib2
import urlparse
import BeautifulSoup as bs
import requests

def getUrl():
	try:
		return sys.argv[1]
	except IndexError:
		print "Uso:"
		print "\t{0} url_to_crawl\nEjemplos:\n\t{0} http://www.labredes.unlu.edu.ar/".format(sys.argv[0])
		sys.exit()
	except OSError, e:
		print e
		sys.exit()

def main():
	# Tomo link raiz pasado por parametro
	rootLink = getUrl()

	# Inicializo variables con link root
	urlCounter = 1 # COntador de url usado como id
	toCrawl = set([rootLink]) # lista to-do con urls a visitar
	linksData = { # Cada url mapea a su data correspondiente
		rootLink: {
			"id": urlCounter,
			"outlinks": set()
		}
	}

	# webs ya visitadas
	crawled = set()

	# Comienza a crawlear
	while len(toCrawl) > 0 and len(toCrawl) < 50:
		# Tomo un link de la lista de to-do
		parentLink = toCrawl.pop()
		print "Visitando ", parentLink

		# Lo agrego a la lista de crawleados
		crawled.add(parentLink)

		# Itero sobre links externos
		for linkCrawled in getLinks(parentLink):

			# Es nueva URL?
			if linkCrawled not in linksData:
				# Nueva url, incremento contador
				urlCounter += 1
				# Le asigno id e inicializo outlinks
				linksData[linkCrawled] = {
					"id": urlCounter,
					"outlinks": set()
				}
				# Nuevo link a lista to-do
				toCrawl.add(linkCrawled)

			# Agrego outlink url padre
			linksData[parentLink]["outlinks"].add(linksData[linkCrawled]["id"])

	print "-" * 50
	print "Total paginas crawleadas:", len(toCrawl)
	print "Paginas visitadas"
	for l in linksData:
		print l + ": " + "outlinks = " + str(len(linksData[l]["outlinks"]))

def getLinks(url, url_instance = None, n = None):
	extractedLinks = []

	if url_instance is not None:
		urlContent = url_instance
	else:
		try:
			urlContent = urllib2.urlopen(url)
		except (ValueError, urllib2.HTTPError, urllib2.URLError) as e:
			return []

	# Si no es html, no tiene sentido buscar tags <a>, nunca los va a haber
	if not 'text/html' in urlContent.info().getheader('Content-Type'):
		return []

	soup = bs.BeautifulSoup(urlContent)
	for linkTag in soup.findAll('a'):
		actualLink = linkTag.get('href')
		# Ignoro links sin href
		if actualLink is not None:
			# Ignoro links que comienzan con simbolo '#' (secciones)
			if not actualLink.startswith("#"):

				# Si es link relativo, se arma el link absoluto con url padre
				if isRelativeUrl(actualLink):
					actualLink = urlparse.urljoin(url, actualLink)

				# Agrego links a lista de links hijos
				extractedLinks.append(actualLink)
	
	return extractedLinks[:n]

def isRelativeUrl(url):
	return not bool(urlparse.urlparse(url).netloc)

def isHtml(url):
	return "text/html" in requests.head(url).headers['Content-Type']

if __name__ == '__main__':
	main()


