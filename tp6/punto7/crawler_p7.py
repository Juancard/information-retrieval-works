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
	todoList = {}
	doneList = []
	todoList[getUrl()] = []
	while todoList and len(todoList) < 50:
		print "tam: ", len(todoList)
		htmlPage = urllib2.urlopen(urlGiven)
		soup = BeautifulSoup(htmlPage)
		links = soup.findAll('a', attrs={'href': re.compile("^http://")})
		for l in links:
			if l in doneList:

				if l in todoList:
	
	print todoList



if __name__ == "__main__":
	main()