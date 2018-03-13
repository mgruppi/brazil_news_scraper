# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 18:32:55 2018
Reads in br news files (plain text)
@author: Maurício Gruppi
"""

import os
import BR_metrics as mtr


class NewsArticle:
    def __init__(self,title_,text_,date_,src_):
        self.title = title_
        self.text = text_
        self.date = date_
        self.source = src_
     
    def __str__(self):
        return ("%s,%s,%s" % (self.date,self.source,self.title))

class NewsSource:
    def __init__ (self,name_):
        self.name = name_
        self.num_articles = 0
        self.first = 0
        self.latest = 0
    
    def add_article(self,article):
        self.num_articles += 1
        
        if self.first == 0 or article.date < self.first:
            self.first = article.date
        if self.latest == 0 or article.date > self.latest:
            self.latest = article.date
            
    def __str__(self):
        return (self.name + ", " + str(self.num_articles) + ", " + self.first + ", " + self.latest)
    
    def __lt__(self,other):
        return (self.name < other.name)
            
    def __eq__(self, other):
        return self.name == other.name
            

#GET THE SMOG grade for a text string https://en.wikipedia.org/wiki/SMOG
def get_SMOG(text_in):
    mtr.get_SMOG(text_in)

      
def make_article(f_path):

    #list should be ["root"/"date"/"source"/"file"]
    #/data/data/br_news_plain_text/2018-02-26/g1/noticia.txt
    #print(f_path)
    #print(s_file)
    
    fin = open(f_path,'r')
    text_ = ""
    #FIRST LINE IS TITLE
    title_line = fin.readline()
    for line in fin:
        text_ += line
    
    fin.close()
    
    f_path = f_path.replace('\\','/')
    s_file = f_path.split("/") #split at / 
    
    article = NewsArticle(title_line,text_,s_file[len(s_file)-3],s_file[len(s_file)-2])
    
    #print(str(article))
    return article
    
    
    

def main():
    #use unicode path for os.walk
    path = u'/data/data/br_news_plain_text/'
    print("(BR) News profiling")
    print("Walking " + path)
    articles = []
    sources = []
    
    filter_first = '2017-12-01'
    
    for dir_name, sub_dir_list, file_list in os.walk(path):
		#print("Subdirs: " + str(len(sub_dir_list)))
        for fname in file_list:
            article_ = make_article(dir_name+"/"+fname)
            if article_.date < filter_first:
                continue
            articles.append(article_)
            src = NewsSource(article_.source)
            if not src in sources:
                src.add_article(article_)
                sources.append(src)
            else:
                for i in range(0,len(sources)):
                    if sources[i] == src:
                        sources[i].add_article(article_)
                
            
    
    print "Articles:",len(articles)
    print "Sources:", len(sources)
    
    sources = sorted(sources)
    
    for src in sources:
        print str(src)
            
    

if __name__ == '__main__':
    main()

