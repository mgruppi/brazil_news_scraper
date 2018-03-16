# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 18:32:55 2018
Reads in br news files (plain text)
@author: Maurício Gruppi
"""

import os

class NewsArticle:
    def __init__(self,id_,title_,text_,date_,src_,src_type_=""):
        self.id = id_
        self.title = title_
        self.text = text_
        self.date = date_
        self.source = src_
        self.src_type = src_type_
     
    def __str__(self):
        return ("%s,%s,%s" % (self.date,self.source,self.title))

class NewsSource:
    def __init__ (self,name_,type_=""):
        self.name = name_
        self.num_articles = 0
        self.first = 0
        self.latest = 0
        self.type=type_
    
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
                 
def make_article(f_path,fname):

    #list should be ["root"/"date"/"source"/"file"]
    #/data/data/br_news_plain_text/20180226/g1/noticia.txt
    #print(f_path)
    #print(s_file)
    
    list_fake = ["correiodopoder","gazetasocial","pensabrasil","saudevidaefamilia","diariodobrasil","folhapolitica","jornaldopais"]
    list_real = ["g1","folhadespaulopoder","istoe","bbcbrasil","reutersbr","exame","extra","elpaisbrasil","otempo"]
    list_satire = ["sensacionalista","joselittomuller","piauiherald","enfu","diariopernambucano"]
    
    fin = open(f_path,'r')
    text_ = ""
    #FIRST LINE IS TITLE
    title_line = fin.readline()
    for line in fin:
        text_ += line
    
    fin.close()
    
    f_path = f_path.replace('\\','/')
    s_file = f_path.split("/") #split at / 
    
    srctype = ""
    srcname = s_file[len(s_file)-2]
    if srcname in list_real:
        srctype = "real"
    elif srcname in list_fake:
        srctype = "fake"
    elif srcname in list_satire:
        srctype = "satire"
    article = NewsArticle(fname,title_line,text_,s_file[len(s_file)-3],srcname,srctype)
    return article
    

def write_clean_file(article,out_path):
    title_out = out_path+"clean/title/"+article.src_type+'/'+article.id
    fout = open(title_out,"w")
    fout.write(article.title)
    fout.close()
    
    text_out = out_path+"clean/text/"+article.src_type+'/'+article.id
    fout = open(text_out,"w")
    fout.write(article.text)
    fout.close()

def makedirs(out_path):
    if not os.path.exists(out_path+"clean/"):
		os.makedirs(out_path+"clean/")
    if not os.path.exists(out_path+"clean/title/"):
        os.makedirs(out_path+"clean/title/")
    if not os.path.exists(out_path+"clean/title/fake"):
        os.makedirs(out_path+"clean/title/fake")
    if not os.path.exists(out_path+"clean/title/real"):
        os.makedirs(out_path+"clean/title/real")
    if not os.path.exists(out_path+"clean/title/satire"):
        os.makedirs(out_path+"clean/title/satire")
    if not os.path.exists(out_path+"clean/text/"):
        os.makedirs(out_path+"clean/text/")
    if not os.path.exists(out_path+"clean/text/fake"):
        os.makedirs(out_path+"clean/text/fake")
    if not os.path.exists(out_path+"clean/text/real"):
        os.makedirs(out_path+"clean/text/real")
    if not os.path.exists(out_path+"clean/text/satire"):
        os.makedirs(out_path+"clean/text/satire")

def main():
    #use unicode path for os.walk
    path = u'/data/data/br_news_plain_text/'
    out_path = u'/data/data/br_news_clean/'
    print("(BR) News profiling")
    print("Walking " + path)
    articles = []
    sources = []
    filter_first = '20180215'
    filter_last = '20180315'
    
    makedirs(out_path)
    
    for dir_name, sub_dir_list, file_list in os.walk(path):
		#print("Subdirs: " + str(len(sub_dir_list)))
        for fname in file_list:
            article_ = make_article(dir_name+"/"+fname,fname)
            if article_.date < filter_first or article_.date > filter_last:
                continue
            if article_.src_type == "fake" or article_.src_type == "real" or article_.src_type == "satire":
                write_clean_file(article_,out_path)
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

