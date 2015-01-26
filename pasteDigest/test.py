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

sys.path.append(settings.BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pasteDigest.settings'
import django
django.setup()
from main.models import keyword as keyword_db, pastebin_log as paste_log_db


KEYWORDS = {
    'hack':5,
    'anonymous':5,
    'egypt':10,
    'pass':10,
    'leak':5,
    'mysql':5,
    'database':5,
    'gmail.com':1,
    'hotmail.com':1,
    'yahoo.com':1,
    'live.com':1,
    'mail.ru':1,
    'gov.eg':20,
    
}

con = sqlite3.connect(settings.BASE_DIR+'/db.sqlite3')
#con.text_factory = unicode
        
        
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        print("Exitting gracefully")
        con.close()
        sys.exit(0)
        
        
WEBSITE = 'http://www.pastebin.com'
url = ''

signal.signal(signal.SIGINT, signal_handler)


def update_keyword_db(con, key_word, count, url=None):
    
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
  

#pattern matching function
def KMP(text, pattern):
 
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

#This function should take as input the content of the pastebin and the a word list
#The function should measure the distance between the content and the word list
#The function should then return an int value which is the distance
def get_weight(content, word_list, url=None):
    wieght = 0
    matched_list = []
    global con
    for key in word_list.keys():    
        loc = KMP(content, key)
        count = len(list(loc))
        wieght += count * word_list[key]
        if count>0:
            update_keyword_db(con, key, count,url)
            matched_list.append(key)
    return wieght, matched_list


#This function takes the paste URL i.e., B814g7GD and will return the following data
#time the paste has been create - no_visitors so far - content
def get_paste_details(URL):
    
    time.sleep(1)
    #TO-DO parse the size and the user who created the paste 
    r = requests.get("%s/%s"%(WEBSITE, URL))
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
    content = unicode(content.text)[:100]
    
    return (time_var, no_visitors, content)
    

#This is a boolean function check if a paste already in the db based on its URL 
def check_entry_db(con, table, condition):
    cur = con.cursor()
    query = "SELECT * FROM %s where url=:url" %(table)
    cur.execute(query, {'url': condition})
    rows = cur.fetchall()
    return True if len(rows)>0 else False

def insert_into_db(con, table, data):
    cur = con.cursor()
    if not check_entry_db(con, table, data['url']):
        #query = "INSERT INTO %s\
        #(datetime, title, url, syntax, content, visitors)\
    #VALUES ('%s', '%s', '%s', '%s', '%s', %d)" \
        #%(table, data['datetime'], data['title'].encode('utf-8'), data['url'], data['syntax'], data['content'].encode('utf-8'), data['visitors'])
        
        
        query = 'INSERT INTO %s (datetime, title, url, syntax, content, visitors, wieght) VALUES (:datetime, :title, :url, :syntax, :content, :visitors, :wieght)'%(table)
        cur.execute(query, data)
        con.commit()
        return 1

  

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


def add_relation(matched_list, url):
    post = paste_log_db.objects.get(url=url)
    for key in matched_list:
        k_word = keyword_db.objects.get(name=key)
        k_word.paste_posts.add(post)
        k_word.save()
    return 1
    



def main():
    
    insert_keywords_db(con, KEYWORDS)
    url = 'NOT_STARTED'
    get_paste_details('qQYsb7N7')
    
    
    
    try:
        while True:
            r =  requests.get("http://pastebin.com/archive")
            html=unicode(r.text)
            soup = BeautifulSoup(html)
            table = soup.find('table')
            if table is None:
                print "OPPS, you have been blocked!! .. tyb eh?"
                #if blocked sleep 30 mins and then continue
                time.sleep(60*30)
                continue
            rows = table.find_all('tr')[1:]
            for row in rows[:20]: # We are processing the first 20 rows for now ... to avoid getting blocked from Pastebin
                try:
                    cells = row.find_all('td')
                except:
                    break
                title = unicode(cells[0].a.text)
                url =  cells[0].a['href'][1:]
                syntax = cells[2].a['href'].split('/')[-1]
                if not check_entry_db(con,'main_pastebin_log',url):
                    more_details = get_paste_details(url)
                    data = dict()
                    data['title'] = title
                    data['syntax'] = syntax
                    data['url'] = url
                    data['content'] = more_details[2]
                    data['visitors'] = more_details[1]
                    data['datetime'] = more_details[0].strftime('%Y-%m-%d %H:%M:%S') #'2007-01-01 10:00:00'
                    data['wieght'], matched_list = get_weight(more_details[2], KEYWORDS, url)
                    insert_into_db(con, 'main_pastebin_log', data)
                    add_relation(matched_list, url)
                    
                    print "INSERTED: %s" %(url)
                else:
                    print "Duplicated: %s" %(url)
                    print "Sending a new request..."
                    time.sleep(random.randint(1,4))
                    break
    
        con.commit()
        con.close()
    except Exception, e:
        print e
        print "Paste URL: %s" %(url)
        con.commit()
        con.close()
        print "EXITED"
    
    
if __name__ == '__main__':
    main()