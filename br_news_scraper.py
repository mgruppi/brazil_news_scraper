# -*- coding: utf-8 -*-
"""
@author: Mauricio Gruppi
"""

import sys
import os
import urllib
import urllib2
import json
import feedparser
from bs4 import BeautifulSoup
import schedule
import time
from dateutil import parser
from goose import Goose
import re
import pytz
import unicodedata
import io
import smtplib
import datetime

g = Goose()


class Site:
    def __init__(self,_name,_url):
        self.name = _name
        self.url = _url

def createFile(source, href, title, author, date, articleHTML, articleText):
	#print "Site", source
	# don't save articles which do not have content
	#print articleText
	if (len(articleText)) == 0:
		flog = open("collect.log","a")
		flog.write(str(datetime.datetime.now()) + ": " + source + " null article text\n")
		flog.close()
		#print(str(datetime.datetime.now()) + " null article text")
		return

	day = str(date)
		

	#create file name
	shortTitle = title[0:100]
	fName = source + "--" + day + "--" + shortTitle 
	validFileName = fName + ".txt"
	
	#these strings need to be unicode
	articleHTML = unicode(articleHTML, "utf-8")
	#make json
	d = {"source": source, "link": href, "title": title, "author": author, "published": date, "content": articleText, "html": articleHTML}
	
	#make a directory for the date
	p = "/data/data/br_news/"+day#"./../../data/newscollection/articles/" + day

	if not os.path.exists(p):
		os.makedirs(p)

	#make a directory for the source
	p = p + "/" + source + "/"

	if not os.path.exists(p):
		os.makedirs(p)
    
	#print ("path " + p)
	#print ("file " + validFileName)

	#print "writing out: " + p
	with io.open(p + validFileName, 'w', encoding='utf-8') as f:
		f.write(json.dumps(d, ensure_ascii=False))

	f.close()
    
	#print("wrote file")
    

def RSSfeed(source, url):
	#print "RSS feed"
	feed = feedparser.parse(url)
	#print ("entries " + str(len(feed["entries"])))
	for article in feed["entries"]:
		href = article["link"]
		title = article["title"]
		author = ""
		if 'author' in article:
			author = article["author"]
		date = article["published"]
		
		#print(href)
		#print(title)
		#print(source)

		articleHTML = ""
		if (source == "The New York Times"):
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
  			response = opener.open(href)
  			articleHTML = response.read()
		else:

			request = urllib2.Request(href, headers = {"User-Agent" : "Magic-Browser"})
			response = urllib2.urlopen(request)
			if (response.code != 200):
				continue
			articleHTML = response.read()

		articleText = ""
		
		if (source == "OperaMundi"):
			articleText = article["content"][0]["value"]
			#print(articleText)
			cleanRules = re.compile('<.*?>')
			articleText = re.sub(cleanRules,'',articleText)
			title = title.replace('?','')
			articleHTML = ""
		elif (source == "ObservatorioDaImprensa"):
			articleText = article["content"][0]["value"]
			cleanRules = re.compile('<.*?>')
  			articleText = re.sub(cleanRules, '', articleText)
  			articleText = articleText.strip()
		else:
			articleText = g.extract(url = href).cleaned_text
		
		#could not retrieve article text?
		if articleText == "":
			found_contents = False
			for key,value in article.iteritems():
				if key == "contents":
					found_contents = True
			if found_contents:
				articleText = article["content"][0]["value"]
				cleanRules = re.compile('<.*?>')
				articleText = re.sub(cleanRules, '', articleText)
				articleText = articleText.strip()
			else:
				write_log(source+": missing [contents].", "missing_contents.log")

  		createFile(source, href, title, author, date, articleHTML, articleText)
      
def write_log(msg, log_file = "collect.log"):
	flog = open(log_file,"a")
	flog.write( str(datetime.datetime.now()) + msg + "\n")
	flog.close()
	  
def read_sources():
    sites = []
    fin_sources = open("br_sources.txt","r")
    for line in fin_sources:
        if line[0] == "*":
           # print line
            continue
        line = line.lstrip('#')
        line = line.rstrip('\n')
        line = line.split('@')
        sites.append(Site(line[0],line[1]))
        print line[0]
        #print line[0],"(",line[1],")"
    
    fin_sources.close()
    return sites
        

def main():
  print "Running BR News Collector " + str( datetime.datetime.now())
  sites = read_sources()
  print ("Collecting ")
  for s in sites:
      try:
	  print(s.name)
          RSSfeed(s.name,s.url)
      except:
          print (s.name," did not collect.")
		  #save log
          flog = open("collect.log","a")
          flog.write(str(datetime.datetime.now()))
          flog.write(": "+s.name + " did not collect.\n")
          flog.close()
	
  print "Finished batch. " + str(datetime.datetime.now())
      

  

if __name__ == "__main__":
  main()
  schedule.every().day.at("04:45").do(main)
  schedule.every().day.at("11:53").do(main)
  schedule.every().day.at("17:39").do(main)
  schedule.every().day.at("23:55").do(main)
  while True:
    schedule.run_pending()
    time.sleep(60)
                     
