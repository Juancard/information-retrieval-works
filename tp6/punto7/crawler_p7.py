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
	toCrawl = set([getUrl()])
	crawled = set()
	outlinks = {}
	while len(toCrawl) > 0 and len(toCrawl) < 50:
		linkParent = toCrawl.pop()
		crawled.add(linkParent)
		outlinks[linkParent] = set()
		print "Visitando ", linkParent
		allLinksCrawled = getLinks(linkParent)
		for linkCrawled in allLinksCrawled:
			outlinks[linkParent].add(linkCrawled)
			if not (linkCrawled in crawled or linkCrawled in toCrawl):
				toCrawl.add(linkCrawled)
		print len(toCrawl), "links que tenia: ",len(outlinks[linkParent])

	print "Total paginas crawleadas:", len(toCrawl)
	print "Paginas visitadas"
	for l in outlinks:
		print "Link:", l, "Cantidad de outlinks: ", len(outlinks[l])

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


