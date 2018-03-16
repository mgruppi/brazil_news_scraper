# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 22:33:57 2018

@author: Mauricio Gruppi
Compute features for br news articles
"""

import math
import nltk
from nltk.corpus import mac_morpho
import os

postags = ["ADJ","ADV","ADV-KS","ADV-KS-REL","ART","KC","KS","IN","N","NPROP","NUM","PCP","PDEN","PREP","PROADJ","PRO-KS","PROPESS","PRO-KS-REL","PROSUB","V","VAUX","CUR","|EST","|AP","|DAD","|TEL","|DAT","|HOR","|+","|!"]

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

def get_word_count(s_text):
    #returns total word count, unique word count
    s = s_text.split()
    unique_words = []
    total_words = 0
    for word in s:
        word = word.strip("\n").strip('.')
        word = word.lower()
        total_words += 1
        if not word in unique_words:
            unique_words.append(word)
    return total_words, len(unique_words)

def get_TTR(s_text):
    n_total, n_unique = get_word_count(s_text)
    return float(n_unique)/n_total

def get_sentence_count(s_text):
    c_sentences = 0
    end_of_sentence = ['.','!',';','?']
    #print("len",len(s_text))
    for i in range(0,len(s_text)):
        if s_text[i] in end_of_sentence:
            c_sentences += 1
        elif s_text[i] == "\n" and not s_text[i-1] in end_of_sentence:
            c_sentences +=1
    return max(1,c_sentences)
        
def get_stopwords_count(text):
    stopwords = nltk.corpus.stopwords.words('portuguese')
    text_split = text.split(" ")
    s_count = 0
    for word in text_split:
        word = word.strip()
        word = word.lower()
        word = word.decode('utf8')
        if word in stopwords:
            s_count += 1
    return s_count

def get_avg_word_length(text):
    text = text.decode('utf8')
    text = text.split()
    n_words = len(text)
    if n_words == 0:
        return 0
    nsum = 0
    for word in text:
        word = word.strip('\n').strip().strip('.').strip('!').strip('?').strip(',')
        nsum += len(word)
    return float(nsum)/(n_words)



    
    

def get_syllables_count(word):
    #MAKE SURE word is DECODED WITH UTF-8 (word.decode('utf8'))
    #Counts vowels and identify semi-vowels in a word to determine its number of syllables
    #need to decode special characters using utf-8 otherwise word length is messed up
    vowels = ['a'.decode('utf8'),'á'.decode('utf8'),'é'.decode('utf8'),'í'.decode('utf8'),'ó'.decode('utf8'),'ú'.decode('utf8'),'â'.decode('utf8'),'ê'.decode('utf8'),'ô'.decode('utf8'),'ã'.decode('utf8'),'õ'.decode('utf8')]
    decreasing_diphthong = ['i'.decode('utf8'),'u'.decode('utf8'),'e'.decode('utf8'),'o'.decode('utf8')]
    syllables = 0
    for i in range(0, len(word)):
        #print(word[i],'q')
        if word[i] in vowels:
            syllables += 1
        elif word[i] in decreasing_diphthong:
            if i == 0: #cannot be a decreasing diphthong because there's no possible vowel before it
                syllables += 1
            elif not word[i-1] in vowels and not word[i-1] in decreasing_diphthong: #checking for decreasing diphthong
                if word[i] == 'u': #potential growing diphthong
                    if not word[i-1] == 'q' and not word[i-1] == 'g':
                        syllables += 1
                else:
                    syllables += 1
            elif word[i] == 'i': # i does not form decreasing diphthong if succeeded by 'm' or 'n'
                if i < len(word) - 1:
                    if word[i+1] == 'm' or word[i+1] == 'n':
                        syllables += 1    
            elif word[i] == 'e' or word[i] == 'o':
                if word[i-1] in ['a','e','i','o','u']:
                    syllables+=1
    return syllables

def get_polysyllables_count(s_text):
    s = s_text.split()
    n_polysyllables = 0
    #POLYSYLLABLES ARE WORDS WITH 3 OR MORE SYLLABLES
    for word in s:
        word = word.strip("\n").strip('.')
        word = word.lower()
        word = word.decode('utf8')
        syllables = get_syllables_count(word)
        if syllables >= 3:
            n_polysyllables += 1
    return n_polysyllables
    

def get_capitalized_count(text):
    text = text.decode('utf8')
    tkns = nltk.word_tokenize(text)
    c = 0
    for t in tkns:
        c+= int(t.isupper())
    return c
    

def get_SMOG(s_text):
    n_sentences = get_sentence_count(s_text)
    n_polys = get_polysyllables_count(s_text)
    #print("Sentences:",n_sentences)
    #print("Polys:", n_polys)
    smog = 1.0430 * math.sqrt(n_polys * 30/(n_sentences)) + 3.1291
    return smog

def get_unigram_tagger():
    #using mac morpho corpus to train tagger
    #Use unigram tagging (maybe other ones in the future)
    p_train = 0.9
    print "Training unigram tagger using mac mopho corpus... %.2f train" %(p_train)
    tagged_sents = mac_morpho.tagged_sents()
    size = int(len(tagged_sents)*0.9)
    train_sents = tagged_sents[:size]
    test_sents = tagged_sents[size:]
    uni_tagger = nltk.UnigramTagger(train_sents)
    print "Test accuracy =", uni_tagger.evaluate(test_sents)
    return uni_tagger

def get_pos_tagging(text, tagger): #retrieve POS-tagging from title (or text)
    text = text.decode('utf8')
    text = text.lower()
    tkns = nltk.word_tokenize(text) #tokenize
    rs = tagger.tag(tkns)
    return rs

def get_pos_count(pos_tags):
    #Given a pos tagging, get vector with POS count
    c = {} #use a dict to count
    for tag in pos_tags:
        if tag[1] in c.keys():
            c[tag[1]] += 1
        else:
            c[tag[1]] = 1
    
    return c
        
def get_title_features(text,tagger=None):
    word_count = len(text.split())
    stopwords = get_stopwords_count(text)
    avg_wl = get_avg_word_length(text)
    p_stopwords = (1.0*stopwords)/(1.0*word_count)
    caps = get_capitalized_count(text)
    p_caps = float(caps)/word_count
    smog = get_SMOG(text)
    ttr = get_TTR(text)
    
    if tagger == None:
        tagger = get_unigram_tagger()
    pos_tag = get_pos_tagging(text,tagger)
    pos_c = get_pos_count(pos_tag)
    
    #TO DO: Part-of-speech tagging
    return avg_wl,word_count,p_stopwords,p_caps,smog,ttr,pos_c

def runtest():
    fpath = "tests/sample.txt"
    body_text = ""
    title = ""
    fin = open(fpath,'r')
    title = fin.readline()
    for line in fin:
        if line == "\n":
            continue
        body_text += str(line)
    fin.close()
    
    print title
    print body_text
    
    print(get_title_features(title))   


def save_features(article,tagger=None):
    
    avgwl,wc,p_sw,p_caps,smog,ttr,pos_c = get_title_features(article.title,tagger)
    fout = open(u'title_features.csv',"a+")
    fout.write("%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(article.id.encode('utf8'),article.src_type,avgwl,wc,p_sw,p_caps,smog,ttr))
    for k in postags:
        if k in pos_c:
            c = float(pos_c[k])/wc
            fout.write(",%.2f"%(c))
        else:
            fout.write(",")
    fout.write("\n")
    fout.close()
    avgwl,wc,p_sw,p_caps,smog,ttr,pos_c = get_title_features(article.text,tagger)
    fout = open(u'text_features.csv',"a+")
    fout.write("%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(article.id.encode('utf8'),article.src_type,avgwl,wc,p_sw,p_caps,smog,ttr))
    for k in postags:
        if k in pos_c:
            c = float(pos_c[k])/wc
            fout.write(",%.2f"%(c))
        else:
            fout.write(",")
    fout.write("\n")
    fout.close()
    

def main():   
    #runtest()
    path = u'/data/data/br_news_plain_text/'
    print("(BR) News features")
    print("Walking " + path)
    articles = []
    sources = []
    filter_first = '20180215'
    filter_last = '20180315'
    
    #open new file (erase existing one)
    fout = open("title_features.csv","w")
    fout.write("Filename,Type,avg_wl,word_count,p_stopwords,p_caps,smog,ttr")
    for k in postags:
        fout.write(","+k)
    fout.write("\n")
    fout.close()
    fout = open("text_features.csv","w")
    fout.write("Filename,Type,avg_wl,word_count,p_stopwords,p_caps,smog,ttr")
    for k in postags:
        fout.write(","+k)
    fout.write("\n")
    fout.close()
    
    tagger = get_unigram_tagger()

    for dir_name, sub_dir_list, file_list in os.walk(path):
        for fname in file_list:
            article_ = make_article(dir_name+"/"+fname,fname)
            if article_.date < filter_first or article_.date > filter_last:
                continue #skip if out of timeframe or source not in ground truth
            if not (article_.src_type == "fake" or article_.src_type == "real" or article_.src_type == "satire"):
                continue
            save_features(article_,tagger)
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

if __name__ == '__main__':
    main()