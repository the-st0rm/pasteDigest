#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import *
import time
import signal
import sys



con = sqlite3.connect('db.sqlite3')
con.text_factory = str
        
        
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        print("Exitting gracefully")
        con.close()
        sys.exit(0)
        
        
WEBSITE = 'http://www.pastebin.com'

signal.signal(signal.SIGINT, signal_handler)


#This function should take as input the content of the pastebin and the a word list
#The function should measure the distance between the content and the word list
#The function should then return an int value which is the distance
def get_distance(content, word_list):
    pass


#This function takes the paste URL i.e., B814g7GD and will return the following data
#time the paste has been create - no_visitors so far - content
def get_paste_details(URL):
    
    #TO-DO parse the size and the user who created the paste 
    r = requests.get("%s/%s"%(WEBSITE, URL))
    html = r.text.encode('utf-8')
    soup = BeautifulSoup(html)
    
    details1 = soup.find('div', class_='paste_box_line2')
    spans = details1.find_all('span')
    time_var = spans[0]['title'][:details1.span['title'].rfind(' ')]
    time_var = re.sub(r"([0123]?[0-9])(st|th|nd|rd)",r"\1",time_var)
    time_var = datetime.strptime(time_var, "%A %d of %B %Y %I:%M:%S %p")
    
    try:no_visitors = int(spans[1].text)
    except:no_visitors = int(spans[2].text)
    
    #The first 100 chars of the content will be saved to safe some space for time being!
    content = requests.get("%s/raw.php?i=%s" %(WEBSITE, URL))
    content = content.text.encode('utf-8')[:100]
    
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
        
        
        query = 'INSERT INTO %s (datetime, title, url, syntax, content, visitors) VALUES (:datetime, :title, :url, :syntax, :content, :visitors)'%(table)
        cur.execute(query, data)
        con.commit()
        return 1
    



def main():
    try:
        while True:
            r =  requests.get("http://pastebin.com/archive")
            html=r.text.encode('utf-8')
            soup = BeautifulSoup(html)
            table = soup.find('table')
            rows = table.find_all('tr')[1:]
            for row in rows:
                cells = row.find_all('td')
                title = cells[0].a.text.encode('utf-8')
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
                    insert_into_db(con, 'main_pastebin_log', data)
                    print "INSERTED: %s" %(url)
                else:
                    print "Duplicated: %s" %(url)
                    print "Sending a new request..."
                    time.sleep(1)
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