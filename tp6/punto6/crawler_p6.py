# -*- coding: utf-8 -*-
import sys
import os
import re
import urllib2
import BeautifulSoup as bs
import urlparse

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
	urlGiven = getUrl()
	print "Url dada: ", urlGiven
	print "Links hallados: \n","\n".join(getLinks(urlGiven))

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

if __name__ == "__main__":
	main()