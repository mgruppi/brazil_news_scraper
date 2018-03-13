# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 22:33:57 2018

@author: Mauricio Gruppi
compute metrics for br news articles
"""

import math


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
    
    print "unique:",n_unique," | total:",n_total
    
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
    
    return c_sentences
        

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
    

def get_SMOG(s_text):
   
    n_sentences = get_sentence_count(s_text)
    n_polys = get_polysyllables_count(s_text)
    
    
    print("Sentences:",n_sentences)
    print("Polys:", n_polys)
    
    smog = 1.0430 * math.sqrt(n_polys * 30/(n_sentences)) + 3.1291
    
    return smog