#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import *
import time
import signal
import sys
import random
import sys
import settings
import os
import threading

sys.path.append(settings.BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pasteDigest.settings'
import django
django.setup()
from main.models import keyword as keyword_db, pastebin_log as paste_log_db


KEYWORDS = {
    'hack':5,
    'anonymous':5,
    'egypt':10,
    'password':20,
    'leak':5,
    'mysql':5,
    'database':5,
    '@gmail.com':1,
    '@hotmail.com':1,
    '@yahoo.com':1,
    '@live.com':1,
    '@aol.com':1,
    '@mail.ru':1,
    'gov.eg':20,
    'brazzers':-300,
    'porn':-500,
    'minecraft':-500,
    
}

PATTERNS = {'[0-7]\d\d-\d\d-\d\d\d\d(\s+)':[100, "ssn"]}
con = sqlite3.connect(settings.BASE_DIR+'/db.sqlite3')

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        print("Exitting gracefully")
        con.close()
        sys.exit(0)
 

def insert_keywords_db(con, keywords):
    cur = con.cursor()
    for k in keywords.keys():
        data = dict()
        data['name'] = k
        data['weight'] = keywords[k]
        data['count'] = 0
        query = "INSERT INTO main_keyword (name, weight, reps) SELECT :name, :weight, :count WHERE NOT EXISTS ( SELECT name from main_keyword WHERE name=:name) LIMIT 1"
        cur.execute(query, data)
    con.commit()
    return 1


signal.signal(signal.SIGINT, signal_handler)


class pastebin_digest(threading.Thread):
    def __init__(self, keywords, sqlite_file, patterns=None,shared_lock=None):
        threading.Thread.__init__(self)
        
        self.main_url = "http://pastebin.com/archive"
        self.paste_url = 'http://www.pastebin.com'
        self.word_list = keywords
        self.patterns = patterns
        self.sqlite_file = sqlite_file
        
    def crawl_main(self, ):
        try:
            r =  requests.get(self.main_url) #sometime I get this error error(54, 'Connection reset by peer')
        except Exception, e:
            print 'Exception: ',
            print e
            return None
            
        html=unicode(r.text)
        soup = BeautifulSoup(html)
        table = soup.find('table')
        if table is None:
            print "OPPS, you have been blocked..!!"
            #if blocked sleep 30 mins and then continue
            time.sleep(60*30)
            return None
        else:
            rows = table.find_all('tr')[1:]
            return rows
            
    def __check_entry_db(self, table, condition):
        cur = self.con.cursor()
        query = "SELECT * FROM %s where url=:url" %(table)
        cur.execute(query, {'url': condition})
        rows = cur.fetchall()
        return True if len(rows)>0 else False   
        
    def __insert_into_db(self, table, data):
    #TO-DO Change this to use Django interface !!
        cur = self.con.cursor()
        if not self.__check_entry_db(table, data['url']):
            #query = "INSERT INTO %s\
            #(datetime, title, url, syntax, content, visitors)\
        #VALUES ('%s', '%s', '%s', '%s', '%s', %d)" \
            #%(table, data['datetime'], data['title'].encode('utf-8'), data['url'], data['syntax'], data['content'].encode('utf-8'), data['visitors'])
            
            
            query = 'INSERT INTO %s (datetime, title, url, syntax, content, visitors, wieght) VALUES (:datetime, :title, :url, :syntax, :content, :visitors, :wieght)'%(table)
            cur.execute(query, data)
            self.con.commit()
            return 1
            
    def __KMP(self, text, pattern):
 
        '''Yields all starting positions of copies of the pattern in the text.
        Calling conventions are similar to string.find, but its arguments can be
        lists or iterators, not just strings, it returns all matches, not just
        the first one, and it does not need the whole text in memory at once.
        Whenever it yields, it will have read the text exactly up to and including
        the match that caused the yield.'''
     
        # allow indexing into pattern and protect against change during yield
        pattern = list(pattern)
     
        # build table of shift amounts
        shifts = [1] * (len(pattern) + 1)
        shift = 1
        for pos in range(len(pattern)):
            while shift <= pos and pattern[pos] != pattern[pos-shift]:
                shift += shifts[pos-shift]
            shifts[pos+1] = shift
     
        # do the actual search
        startPos = 0
        matchLen = 0
        for c in text:
            while matchLen == len(pattern) or \
                  matchLen >= 0 and pattern[matchLen] != c:
                startPos += shifts[matchLen]
                matchLen -= shifts[matchLen]
            matchLen += 1
            if matchLen == len(pattern):
                yield startPos
    
    def crawl_paste(self, URL):
        time.sleep(1)
        #TO-DO parse the size and the user who created the paste 
        r = requests.get("%s/%s"%(self.paste_url, URL))
        html = unicode(r.text)
        soup = BeautifulSoup(html)
        
        details1 = soup.find('div', class_='paste_box_line2')
        try:
            spans = details1.find_all('span')
        except:
            time_var = datetime(1900,1,1,1,0)
            no_visitors=0
            content = "Paste has been removed!"
            return (time_var, no_visitors, content)
        time_var = spans[0]['title'][:details1.span['title'].rfind(' ')]
        time_var = re.sub(r"([0123]?[0-9])(st|th|nd|rd)",r"\1",time_var)
        time_var = datetime.strptime(time_var, "%A %d of %B %Y %I:%M:%S %p")
        
        try:no_visitors = int(spans[1].text)
        except:no_visitors = int(spans[2].text)
        
        #The first 100 chars of the content will be saved to safe some space for time being!
        content = soup.find(id='paste_code')  
        content = unicode(content.text)
        
        return (time_var, no_visitors, content)
    
    def __update_keyword_db(self, key_word, count, url=None):
    
        k_word = keyword_db.objects.filter(name=key_word)
        if len(k_word) >1:
            return -1
        elif len(k_word)==1:
            k_word[0].reps = k_word[0].reps+1
            #k_word[0].paste_posts.add(paste_log_db.objects.get(url=url))
            k_word[0].save()
            return 0
        elif len(k_word)==0:
            k_word = keyword_db(name=key_word,count=count)
            k_word.save()
            #k_word.add(paste_log_db.objects.get(url=url))
            return 0
        #cur = con.cursor()
        #data = dict()
        #data['name']=key_word
        #data['count']=count
        #
        #query = 'UPDATE main_keyword SET counter += :count where name=:name'
        #cur.execute(query, data)
        #con.commit()
        return 1
 
    def __get_pattern(self, content, url):
        weight = 0
        matched_list = set()
        for key in self.word_list.keys():    
            loc = self.__KMP(content, key)
            count = len(list(loc))
            weight += count * self.word_list[key]
            if count>0:
                self.__update_keyword_db(key, count, url)
                matched_list.add(key)
        return weight, matched_list
    
    def __get_regex(self, content, url):
        weight = 0
        matched_list = set()
        if self.patterns:    
            for pattern in self.patterns.keys():
                re_comp =  re.compile(pattern)
                result = re_comp.finditer(content) # I don't know WHY THE HELL IT IS NOT WORKING with findall or SEARCH .. it only matched one value
                count = len(list(result))
                weight+= count * self.patterns[pattern][0]
                if count >0:
                    #TO-DO: update that the number of pattern was found in the database
                    matched_list.add(self.patterns[pattern][1])
            return weight, matched_list
        
    def __add_relation(self, matched_list, url):
        post = paste_log_db.objects.get(url=url)
        for key in matched_list:
            k_word = keyword_db.objects.get(name=key)
            k_word.paste_posts.add(post)
            k_word.save()
        return 1
    def get_weight(self, content, url):
        weight = 0
        matched_list = []
        content = content.lower()
        
        weight_pattern, matched_list_pattern = self.__get_pattern(content, url)
        weight_regex, matched_list_regex = self.__get_regex(content, url)
        weight = weight_pattern + weight_regex
        
        
        return weight, matched_list_pattern, matched_list_regex
    
    def run(self, ):
        self.con = sqlite3.connect(settings.BASE_DIR+'/'+self.sqlite_file)
        try:
            while True:
                rows = self.crawl_main()
                if not rows:
                    continue
                for row in rows[:20]: # We are processing the first 20 rows for now ... to avoid getting blocked from Pastebin
                    try:
                        cells = row.find_all('td')
                    except:
                        break
                    title = unicode(cells[0].a.text)
                    url =  cells[0].a['href'][1:]
                    syntax = cells[2].a['href'].split('/')[-1]
                    if not self.__check_entry_db('main_pastebin_log',url):
                        more_details = self.crawl_paste(url) #Ef7N9JYg-QxejwkNU-pRJmtyNJ
                        data = dict()
                        data['title'] = title
                        data['syntax'] = syntax
                        data['url'] = url
                        data['content'] = more_details[2]
                        data['visitors'] = more_details[1]
                        data['datetime'] = more_details[0].strftime('%Y-%m-%d %H:%M:%S') #'2007-01-01 10:00:00'
                        data['wieght'], matched_list_pattern, matched_list_regex = self.get_weight(more_details[2], url)
                        
                        
                        self.__insert_into_db('main_pastebin_log', data)
                        self.__add_relation(matched_list_pattern, url)
                        
                        print "INSERTED: %s" %(url)
                    else:
                        print "Duplicated: %s" %(url)
                        print "Sending a new request..."
                        time.sleep(random.randint(1,4))
                        break
        
        except Exception, e:
            print e
            print "Paste URL: %s" %(url)
            con.commit()
            con.close()
            print "EXITED"

    


def main(): 
    insert_keywords_db(con, KEYWORDS)
    pd = pastebin_digest(KEYWORDS, 'db.sqlite3', PATTERNS)
    pd.start()
    pd.join()
    return

if __name__ == '__main__':
    main()