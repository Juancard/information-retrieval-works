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
		isValidUrl, requestInstance = validateUrl(linkParent, html_only = True)
		if isValidUrl:
			crawled.add(linkParent)
			outlinks[linkParent] = set()
			print "Visitando ", linkParent
			allLinksCrawled = getLinks(urlInstance = requestInstance, n=50)
			for linkCrawled in allLinksCrawled:
				if "#" in linkCrawled: print linkCrawled
				if isRelativeUrl(linkCrawled):
					linkCrawled = urlparse.urljoin(linkParent, linkCrawled)
				outlinks[linkParent].add(linkCrawled)
				if linkCrawled not in crawled and linkCrawled not in toCrawl:
					toCrawl.add(linkCrawled)

	print "Total paginas crawleadas:", len(toCrawl)
	print "Paginas visitadas"
	for l in outlinks:
		print "Link:", l, "Cantidad de outlinks: ", len(outlinks[l])

def getLinks(url = None, urlInstance = None, n = None):
	extractedLinks = []
	html = None

	if urlInstance:
		html = urlInstance
	elif url is not None:
		try:
			html = urllib2.urlopen(url)
		except (ValueError, urllib2.HTTPError, urllib2.URLError) as e:
			return extractedLinks

	if html is not None:
		soup = bs.BeautifulSoup(html)
		for linkTag in soup.findAll('a'):
			actualLink = linkTag.get('href')
			if actualLink is not None:
				extractedLinks.append(actualLink)

	return extractedLinks[:n]

def isRelativeUrl(url):
	return not bool(urlparse.urlparse(url).netloc)

def validateUrl(url, html_only=False):
	# Devuelve arreglo con dos valores
	# primer valor: booleano si es o no url valida
	# segundo valor: instancia generada por request a servidor
	try:
		html = urllib2.urlopen(url)
		if html_only: return [isHtml(html), html]
		else: return [True, html]
	except (ValueError, urllib2.HTTPError, urllib2.URLError) as e:
		return [False, None]


def isHtml(urllib2Instance):
	httpHeader = urllib2Instance.info()
	return "text/html" in httpHeader.getheader('Content-Type')

if __name__ == '__main__':
	main()