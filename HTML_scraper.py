# -*- coding: utf-8 -*-
"""
@author: Maurício Gruppi
HTML news scraper
"""

from requests import get
from bs4 import BeautifulSoup
import datetime
import os
import io
import json

class Article:
    def __init__(self,title,text,author,date,source):
        self.title = title
        self.text = text
        self.author = author
        self.date = date
        self.source = source
     
def get_month_number(month_name):
    month_name = month_name.lower()
    m = ["janeiro","fevereiro","março","abril","maio","junho","agosto","setembro","outubro","novembro","dezembro"]
    for i in range(0,len(m)):
        if m[i].decode('utf8') == month_name:
            return i+1
    print("INVALID MONTH NAME")
    return -1
        
def create_file(source, href, title, author, date, articleHTML, articleText, root="/data/data"):
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
    #clean up title
    fName = fName.replace('/','')
    fName = fName.replace('&','')
    fName = fName.replace('%','')
    fName = fName.replace(":",'')
    fName = fName.replace('*','')
    fName = fName.replace('\\','')
    fName = fName.replace('?','')
    fName = fName.replace('%','')
    fName = fName.replace('"','')
    fName = fName.replace("'",'')
    fName = fName.replace(',','')
    fName = fName.replace(';','')
    validFileName = fName + ".txt"
	
    #these strings need to be unicode
    #articleHTML = unicode(articleHTML, "utf-8")
    #make json
    d = {"source": source, "link": href, "title": title, "author": author, "published": date, "content": articleText, "html": articleHTML}
	
    #make a directory for the date
    p = root+"/br_news/"+day#"./../../data/newscollection/articles/" + day

    if not os.path.exists(p):
        os.makedirs(p)

    p = p + "/" + source + "/"

    if not os.path.exists(p):
        os.makedirs(p)

    #print "writing out: " + p
    with io.open(p + validFileName, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False))

    f.close()
    

def get_jornaldacidade_list(page=0):
    #Jornal da cidade shows 30 news articles per page
    #?&start=<num> determines the starting article from the list (0...n)
    #root_url = "https://www.jornaldacidadeonline.com.br/noticias"
    search_url = "https://www.jornaldacidadeonline.com.br/noticias/politica/?&start="+str(page)
    articles = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find('div',class_='container container--flex')
        articles = large_div.find_all('a',class_='widget__image')
        #articles = html_soup.find_all('article', class_='widget widget--lg') #articles are in div class 'featured-posts'
        #article tags have classes widget widget--(xl,lg,md,sm)
        #articles = html_soup.find_all('a',class_='widget__image')
    except:
        print("(Jornal da cidade) failed to get list.")
    
    #this gives a list of (30) articles url to search for
    return articles

def get_jornaldacidade_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        content = html_soup.find('main',class_='content')
        title = content.h1
        date = content.small
        author = content.span
        text = content.find('div',class_='post__description')
        article_html = content.text
        ad_divs = text.find_all('div',class_='ads ads--post-exibicao-conteudo')
        for ad_div in ad_divs:
            ad_div.decompose() #remove ads
    
        #format date yyymmdd
        s_date = date.text.split()
        h_date = s_date[2].split(":")
        tmp_date = s_date[0].split('/')
        s_date = tmp_date[2]+tmp_date[1]+tmp_date[0]+h_date[0]+h_date[1]
        
        
        create_file("jornaldacidade",article_url,title.text,author.text,s_date,article_html,text.text)
    except:
        print("Failed to get article: " + article_url)
        

def scrape_jornaldacidade(pages=1):
    print "JornalDaCidade"
    for i in range(0,pages):
        url_list = get_jornaldacidade_list(i*30)
        if len(url_list) == 0:
            print("jornaldacidade: empty list")
        for url in url_list:
            get_jornaldacidade_article(url["href"])
    

############ REUTERS ################
    
def get_brreuters_list(page=0):
    root_url = "https://br.reuters.com"
    search_url = "https://br.reuters.com/news/archive/domesticNews?page=" + str(page)
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find_all('div',class_='headlineMed standalone')
    except:
        print("(Reuters BR) Get list failed.")
    
    #reuters br gives a list of 20 articles
    for div in large_div:
        url_list.append(root_url+div.a["href"])
    
    return url_list

def get_brreuters_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        upper_container = html_soup.find('div',class_='upper-container_3g5eM')
        headline = upper_container.find('h1')
        title = headline.text
        date = upper_container.find('div',class_='date_V9eGk')
        s_date = date.text.split('/')
        h_date = datetime.datetime.strptime(s_date[1],"  %I:%M %p ")
        d_date = datetime.datetime.strptime(s_date[0], "%B %d, %Y ")
        date = str(d_date.year) + "%02d"%(d_date.month)+"%02d"%(d_date.day)+"%02d"%(h_date.hour)+"%02d"%(h_date.minute)
        
        lower_container = html_soup.find('div',class_="lower-container")
        author = lower_container.find('p',class_="byline_31BCV")
        author = author.text
        
        article_body = html_soup.find('div',class_="body_1gnLA")
        p_list = article_body.find_all('p')
        text = ""
        for p in p_list:
            text+=p.text
        

        create_file("reutersbr",article_url,title,author,date,article_body.text,text)

        
        
        #create_file("reutersbr",article_url,title.text,author.text,s_date,article_html,text.text)
    except:
        print("Couldn't get article: "+article_url)
    

def scrape_reutersbr(pages=1):
    print "ReutersBR"
    for i in range(0,pages):
        url_list = get_brreuters_list(i)
        if len(url_list) == 0:
            print("(Reuters BR): empty list")
        for url in url_list:
            get_brreuters_article(url)
    

#================ ESQUERDA DIARIO ====================
def get_esquerdadiario_list(page=0):
    root_url = "http://esquerdadiario.com.br/"
    search_url = "http://www.esquerdadiario.com.br/Politica?debut_articulos2="+str(page)+"#pagination_articulos2"
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find_all('div',class_='noticia')
    except:
        print("(Esquerdadiario) Get list failed.")
    
    #list of 24 articles per page
    for div in large_div:
        url_list.append(root_url+div.a["href"])
    
    return url_list


def get_esquerdadiario_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        headline = html_soup.find('div',class_="header-articulo")
        title = headline.h1.text
        
        #this site is not locale sensitive, so we need to change locale to pt_BR
        date = html_soup.find('span',style="color: #364b67;").text
        s_date = date.split()
        m_date = get_month_number(s_date[3])
        date = "2018"+"%02d"%(int(m_date))+"%02d"%(int(s_date[1]))+"0000"
        
        author_div = html_soup.find('div',class_='autor-articulo')
        author = author_div.find('p').text
        article = html_soup.find('div', class_='articulo')
        #Remove "Topicos relacionados" div
        topicos = article.find('div',class_='temas-relacionados')
        topicos.decompose()
        text=""
        plist = article.find_all('p')
        
        for p in plist:
            text+=p.text
        create_file("esquerdadiario",article_url,title,author,date,"<empty>",text)
    except:
        print("Couldn't get article: "+article_url)
    
    

def scrape_esquerdadiario(pages=1):
    print "EsquerdaDiario"
    for i in range(0,pages):
        url_list = get_esquerdadiario_list(i*24)
        if len(url_list) == 0:
            print("(Esquerda diario): empty list")
        for url in url_list:
            get_esquerdadiario_article(url)
            
#======================== SAUDEVIDAEFAMILIA ====================
            
def get_saudevidaefamilia_list(page=1):
    search_url = "https://saudevidaefamilia.com/page/"+str(page)
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find('div',class_='g1-collection-viewport')
        alist = large_div.find_all('a',class_='g1-frame')
        
        for a in alist:
            url_list.append(a["href"])
        
        return url_list
    except:
        print("(Saudevidaefamilia) Get list failed.")
   

def get_saudevidaefamilia_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        contents = html_soup.find('div',id="content")
        article_body = contents.find('div',class_="entry-content g1-typography-xl")
        headline = contents.find('header',class_='entry-header')
        title=headline.h1.text
        plist = article_body.find_all('p')
        text = ""
        for p in plist:
            text+=p.text
        
        date = html_soup.find('time',class_='entry-date').text
        s_date = date.split()
        s_day = s_date[0]
        s_month = get_month_number(s_date[2])
        s_year = s_date[4].strip(',')
        s_hm = s_date[5].strip().split(':')
        date = s_year + "%02d"%(int(s_month)) + "%02d"%(int(s_day)) + s_hm[0]+s_hm[1]
        
        author = html_soup.find('span',class_='entry-author').strong.text
        
        
        create_file("saudevidaefamilia",article_url,title,author,date,"<empty>",text)
    except IOError as e:
        print "IO ERROR:({0}) {1}".format(e.errno,e.strerro)
    except:
        print("Couldn't get article: "+article_url)

def scrape_saudevidaefamilia(pages=1):
    print "saudevidaefamilia"
    for i in range(0,pages):
        url_list = get_saudevidaefamilia_list(i)
        if len(url_list) == 0:
            print("(saudevidaefamilia): empty list")
        for url in url_list:
            get_saudevidaefamilia_article(url)    


##=========== JORNAL DO PAIS =============
def get_jornaldopais_list(page=2): #this sites has issues with scraping the first page (it's different from the rest)
    search_url = "https://www.jornaldopais.com.br/page/"+str(page)
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find('div',class_='td-ss-main-content')
        alist = large_div.find_all('h3',class_='entry-title td-module-title')
        for a in alist:
            url_list.append(a.a["href"])
        
        return url_list
    except:
        print("(Jornaldopais) Get list failed.")
        
def get_jornaldopais_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        contents = html_soup.find('div',class_="td-ss-main-content")
        article_body = contents.find('div',class_="entry-content g1-typography-xl")
        headline = contents.find('div',class_='td-post-header')
        title=headline.h1.text
       
        date = headline.find('time').text
        s_date = date.split('/')
        date = s_date[2] + s_date[1]+s_date[0]+"0000"

        article_body = contents.find('div',class_="td-post-content")
        plist = article_body.find_all('p',style='text-align: justify;')
        text = ""
        for p in plist:
            text+=p.text
        author="jornaldopais"
     
        create_file("jornaldopais",article_url,title,author,date,"<empty>",text)
    except IOError as e:
        print "IO ERROR:({0}) {1}".format(e.errno,e.strerro)
    except:
        print("Couldn't get article: "+article_url)    
        

def scrape_jornaldopais(pages=1): #Start scraping on page 2
    print "jornaldopais"
    for i in range(2,2+pages):
        url_list = get_jornaldopais_list(i)
        if len(url_list) == 0:
            print("(jornaldopais): empty list")
        for url in url_list:
            get_jornaldopais_article(url)     

#====== DIARIODOBRASIL ======
def get_diariodobrasil_list_politica(page=2): #start from page 2, front page is scraped by rss
    search_url = "https://www.diariodobrasil.org/category/politica/page/"+str(page)
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        alist = html_soup.find_all('article')
        for a in alist[:-5]: #5 last articles are not from the articles page
            url_list.append(a.a["href"])
    
        return url_list
    except:
        print("(diariodobrasil) Get list failed.")
def get_diariodobrasil_list_brasil(page=2): #start from page 2, front page is scraped by rss
    search_url = "https://www.diariodobrasil.org/category/brasil/page/"+str(page)
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        alist = html_soup.find_all('article')
        for a in alist[:-5]: #5 last articles are not from the articles page
            url_list.append(a.a["href"])
    
        return url_list
    except:
        print("(diariodobrasil) Get list failed.")
        
def get_diariodobrasil_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        contents = html_soup.find('div',id="main-content")
        
        
        headline = contents.find('header',class_='entry-header clearfix')
        title=headline.h1.text.strip('\r').strip('\n').strip('\t')
   
        date = contents.find('p',class_='entry-meta').text.strip('\n')
        s_date = date.split('/')
        date = s_date[2] + s_date[1]+s_date[0]+"0000"

        article_body = contents.find('div',id="HOTWordsTxt")
        plist = article_body.find_all('p')
        text = ""
        for p in plist:
            text+=p.text
        author="diariodobrasil"
     
        create_file("diariodobrasil",article_url,title,author,date,"<empty>",text)
    except IOError as e:
        print "IO ERROR:({0}) {1}".format(e.errno,e.strerro)
    except:
        print("Couldn't get article: "+article_url)   

def scrape_diariodobrasil(pages=1):
    print "diariodobrasil"
    for i in range(2,2+pages):
        url_list = get_diariodobrasil_list_politica(i)
        if len(url_list) == 0:
            print("(diariodobrasil): empty list")
        for url in url_list:
            get_diariodobrasil_article(url)
        url_list = get_diariodobrasil_list_brasil(i)
        if len(url_list) == 0:
            print("diariodobrasil: empty list brasil")
        for url in url_list:
            get_diariodobrasil_article(url)

#================ FOLHAPOLITICA ===============
def get_folhapolitica_list(date=datetime.datetime.now(),results=10):
    s_date = datetime.datetime.strftime(date,"%Y-%m-%dT%H:%M:%S")
    search_url="http://www.folhapolitica.org/search?updated-max=%s-03:00&max-results=%s"%(s_date,str(results))
    url_list = []
    try:
        response = get(search_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        large_div = html_soup.find('div',class_='columns-inner')
        alist = large_div.find_all('h3', class_='post-title entry-title')
        for a in alist: #5 last articles are not from the articles page
            url_list.append(a.a["href"])
    
        return url_list
    except:
        print("(folhapolitica) Get list failed.")   

def get_folhapolitica_article(article_url):
    try:
        response = get(article_url, headers = {"Accept-Language": "en-US, en;q=0.5"})
        html_soup = BeautifulSoup(response.text,"html.parser")
        
        contents = html_soup.find('div',id="main")
        
        headline = contents.find('div',class_='post hentry')
        title=headline.h3.text.strip("\n")
          
        date = contents.find('div',class_='date-outer').h2.text.strip("\n")
        s_date = date.split()
        s_day = int(s_date[1])
        s_month = get_month_number(s_date[3])
        s_year = s_date[5]
        date = s_year+ "%02d"%(s_month) + "%02d"%(s_day)+"0000"
        article_body = contents.find('div',class_="post-body entry-content")
        alist = article_body.find_all('a')
        for a in alist:
            a.decompose()
        timg = article_body.find('table',class_='tr-caption-container')
        timg.decompose()
        plist = article_body.find_all('span')
        text = ""
        for p in plist:
            text+=p.text
        author="folhapolitica"     
        create_file("folhapolitica",article_url,title,author,date,"<empty>",text)
    except IOError as e:
        print "IO ERROR:({0}) {1}".format(e.errno,e.strerro)
    except:
        print("Couldn't get article: "+article_url)   
    
def scrape_folhapolitica(date=datetime.datetime.now(),results=50): #use multiples of 50
    print "folhapolitica"
    it = 1
    if results > 50:
        it = results/50
    for i in range(0,it):
        url_list = get_folhapolitica_list((date - datetime.timedelta(days=3*i)),50)
        if len(url_list) == 0:
            print("folhapolitica: empty list")
        for url in url_list:
            get_folhapolitica_article(url)

def main():
    
    #scrape_reutersbr()
    #scrape_esquerdadiario()
    #scrape_jornaldacidade()
    #scrape_saudevidaefamilia(20)
    #scrape_diariodobrasil(10)
    #scrape_jornaldopais(50)
    scrape_folhapolitica(results=1000)
    print("Done.")

if __name__ == '__main__':
    main()

