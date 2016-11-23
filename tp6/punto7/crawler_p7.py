# -*- coding: utf-8 -*-

#-------------crawler---------------------------------#
# Recibe una url por parametro y devuelve
# los outlinks de cada url visitada.
# Adicionalmente genera un grafo con la data obtenida
#-----------------------------------------------------#

import sys
import os
import json
import re
import urllib2
import urlparse
import BeautifulSoup as bs
import requests
import graphviz as gv
import datetime
from collections import OrderedDict

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

def crawl(initialUrlsList, MAX_URLS = sys.maxint):
	# Inicializo variables con urls iniciales
	toCrawl = set(initialUrlsList) # lista to-do con urls a visitar
	linksData = OrderedDict()
	for url in initialUrlsList:
		linksData[url] = {
			"id": len(linksData) + 1,
			"outlinks": set()
		}

	# webs ya visitadas
	crawled = set()

	# Comienza a crawlear
	while len(toCrawl) > 0 and len(linksData) < MAX_URLS:
		# Tomo un link de la lista de to-do
		parentLink = toCrawl.pop()
		print "Visitando ", parentLink

		# Lo agrego a la lista de crawleados
		crawled.add(parentLink)

		# Itero sobre links externos
		for linkCrawled in getLinks(parentLink):

			if len(linksData) >= MAX_URLS: break
			# Es nueva URL?
			if linkCrawled not in linksData:
				# Nueva url, Le asigno id e inicializo outlinks
				linksData[linkCrawled] = {
					"id": len(linksData) + 1,
					"outlinks": set()
				}
				# Nuevo link a lista to-do
				toCrawl.add(linkCrawled)

			# Agrego outlink url padre
			linksData[parentLink]["outlinks"].add(linksData[linkCrawled]["id"])

	return linksData

def main():
	# Tomo link raiz pasado por parametro
	rootLinks = [getUrl()]

	# Hago crawling
	crawled = crawl(rootLinks, MAX_URLS = 50)

	# Muestro resultados en consola
	showResults(crawled)

	# Genero grafo
	print "Grafo guardado en: ", makeGraph(crawled)
	print "-" * 50

def showResults(linksData):
	print "-" * 50
	print "Total paginas recolectadas:", len(linksData)
	print "Paginas visitadas"
	for l in linksData:
		totalOut = len(linksData[l]["outlinks"])
		if totalOut > 0:
			print l + ": \n\t" + "id: " + str(linksData[l]["id"]) + "\n\toutlinks: " + str(totalOut)
	print "-" * 50


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

def makeGraph(linksData):
	# Instancio objeto grafo
	g1 = gv.Digraph(format='svg')

	# Genero nodos y edges a partir de la data recibida
	nodes = []; edges = []
	for l in linksData:
		label1 = str(linksData[l]["id"])
		nodes.append(label1)
		for ol in linksData[l]["outlinks"]:
			label2 = str(ol)
			edges.append((label1, label2))

	# Armo grafo
	add_edges(add_nodes(g1, nodes), edges)

	# Guardo grafo
	timestamp = '{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
	path = 'graphs/%s' % (timestamp)
	filename = g1.render(path+"_graph")

	# Guardo mapeo id a url:
	with open(path + "_mapping", "w") as f:
		for l in linksData:
			f.write("%d: %s\n" % (linksData[l]["id"], l))

	return filename

def add_nodes(graph, nodes):
	for n in nodes:
		if isinstance(n, tuple):
			graph.node(n[0], **n[1])
		else:
			graph.node(n)
	return graph

def add_edges(graph, edges):
	for e in edges:
		if isinstance(e[0], tuple):
			graph.edge(*e[0], **e[1])
		else:
			graph.edge(*e)
	return graph

if __name__ == '__main__':
	main()
