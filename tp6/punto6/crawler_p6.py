import sys
import os
import re
import urllib2
from BeautifulSoup import BeautifulSoup

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
	
	print "Links hallados: "
	html_page = urllib2.urlopen(urlGiven)
	soup = BeautifulSoup(html_page)
	for link in soup.findAll('a'):
	    print link.get('href')

if __name__ == "__main__":
	main()