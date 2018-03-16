# -*- coding: utf-8 -*-
"""
Created on Tue Feb 06 15:04:32 2018

@author: Mauricio Gruppi
BR News articles JSON parser
Parse JSON files and writes plain text files with news article's body text
"""

import json
#import datetime
import os
import sys
#finds an appropriate format for a datetime string in the "published" key
def get_date(s_time):
    s = s_time.encode('ascii') #convert from utf-8 to ascii if needed
    day = 0
    month = 0
    year = 0
    #print("s_time",s_time)
    if ',' in s: #Format is Mon, 01 Jan 2001
        s_list = s.split()
        day = "%02d" % int(s_list[1])
        month = get_month(s_list[2])
        year = s_list[3]
    elif s.count('-') > 2: #Format is 2018-01-21T13_25_06
        #Split it at 'T' to get only the date part (left side)
        s_list = s.split('T')
        #Now split at -
        s_date = s_list[0].split('-')
        day = s_date[2]
        month = s_date[1]
        year = s_date[0]
    elif s.count('-') == 2: #Format is yyyy-mm-dd hh:mm
        s_list = s.split(' ')
        s_list = s_list[0].split('-')
        year = s_list[0]
        month = s_list[1]
        day = s_list[2]
    elif '-' in s or ':' in s: #Format is 01 Feb 2018 01:00:00 -300
        s_list = s.split()
        day = s_list[0]
        month = get_month(s_list[1])
        year = s_list[2]
    else: #Then format is <YEAR><MONTH><DAY><TIME>
        year = s[:4]
        month = s[4:6]
        day = s[6:8]
        
    return day,month,year
        

def get_month(s):
    if s == 'Jan':
        return '01'
    elif s == "Feb" or s == "Fev":
        return '02'
    elif s == 'Mar':
        return '03'
    elif s == 'Abr' or s == 'Apr':
        return '04'
    elif s == 'Mai' or s == 'May':
        return '05'
    elif s == 'Jun':
        return '06'
    elif s == 'Jul':
        return '07'
    elif s == 'Ago' or s == 'Aug':
        return '08'
    elif s == 'Sep' or s == 'Set':
        return '09'
    elif s == 'Oct' or s == 'Out':
        return '10'
    elif s == 'Nov':
        return '11'
    elif s == 'Dec' or s == 'Dez':
        return '12'
    else: #error
        return '00'
    
    
def parse_file(f_path):
    #path = f_path.decode('utf8')
    fin = open(f_path)
    datastore = json.load(fin,encoding='utf8')
    fin.close()
    #== HOUSEKEEPING ==
    datastore['source'] = datastore['source'].lower()
    return datastore

def export_plain_text(f_path):
    datastore = parse_file(f_path)
    
    out_dir = "/data/data/br_news_plain_text" #touch output dir
    if not (os.path.isdir(out_dir)):
        os.mkdir(out_dir)
    
    #touch date dir
    d,m,y = get_date(datastore['published'])
    date_str = y+m+d
    if not (os.path.isdir(out_dir+'/'+date_str)):
        os.mkdir(out_dir+'/'+date_str)
        
    #touch source dir
    source_str = datastore['source'].lower()
    if not (os.path.isdir(out_dir+'/'+date_str+'/'+source_str)):
        os.mkdir(out_dir+'/'+date_str+'/'+source_str)
    
    curr_dir = out_dir+'/'+date_str+'/'+source_str
    #curr_file = source_str+'__'+datastore['title']+'.txt'
    #dir_len = len(curr_dir+'/'+datastore['title']+'.txt')
	
    n_file = datastore['title'][:100]+'.txt'
    curr_file = source_str +"__"+date_str+"__"+ n_file
    curr_file = curr_file.replace('/','')
    curr_file = curr_file.replace('&','')
    curr_file = curr_file.replace('%','')
    curr_file = curr_file.replace(":",'')
    curr_file = curr_file.replace('*','')
    curr_file = curr_file.replace('\\','')
    curr_file = curr_file.replace('?','')
    curr_file = curr_file.replace('%','')
    curr_file = curr_file.replace('"','')
    curr_file = curr_file.replace("'",'')
    curr_file = curr_file.replace(',','')
    curr_file = curr_file.replace(';','')
    

    #if not os.path.isfile(curr_dir+"/"+curr_file):
    fout = open(curr_dir+'/'+curr_file,'w')
    fout.write(datastore['title'].encode('utf8'))
    fout.write("\n")
    fout.write(datastore['content'].encode('utf8'))
    fout.close()
    
    #else:
	#	print("File exists:",str(curr_file.encode('utf8')))


def main():
	path = u'/data/data/br_news'
	count_files = 0

	print "Walking "+path
	for dir_name, sub_dir_list, file_list in os.walk(path):
		#print("Subdirs: " + str(len(sub_dir_list)))
		for fname in file_list:
			count_files += 1
			export_plain_text(dir_name+"/"+fname)

	print("Files:",count_files)

    
    
    
if __name__ == '__main__':
    main()
