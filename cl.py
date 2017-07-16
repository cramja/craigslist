#!/usr/bin/env python
from requests import request as req
from bs4 import BeautifulSoup
from datetime import datetime
#import csv
import sys
import os
import unicodecsv as csv
#import smtplib
#import config

# Craigslist search URL
#BASE_URL = ('http://chicago.craigslist.org/search/'
#            '?sort=rel&areaID=11&subAreaID=&query={0}&catAbb=sss')
query = 'ikea chair'
#BASE_URL=('https://sfbay.craigslist.org/search/sss?query={}&sort=rel&search_distance=10&postal=94025')
BASE_URL=('https://sfbay.craigslist.org/search/fua?query={}&sort=date&srchType=T&search_distance=10&postal=94025')

def get_query_result(search_term):
    search_term = search_term.strip().replace(' ', '+')
    search_url = BASE_URL.format(search_term)
    result = req("get", search_url)
    if result.status_code == 200:
        return result.content
    print "error fetching url {}, {}".format(search_url, result.status_code)
    exit(-1)
 
def parse_results(raw_html):
    results = []
    soup = BeautifulSoup(raw_html, "html5lib")
    rows = soup.find('ul', 'rows').find_all('li', 'result-row')
    for row in rows:
        url = 'http://sfbay.craigslist.org' + row.a['href']
        try:
            price = row.find('span', class_='result-price').get_text()
        except:
            price = -1
        timestamp = row.find('time', class_='result-date').get('datetime')
        create_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        title = row.find_all('a')[1].get_text()
        results.append({'url': url, 'create_date': create_date, 'title': title, 'price': price})
    return results

def write_results(results):
    """Writes list of dictionaries to file."""
    if len(results) == 0:
        print "no results found. This is a script bug"
        exit(1)

    fields = results[0].keys()
    with open('results.csv', 'w') as f:
        dw = csv.DictWriter(f, fieldnames=fields, delimiter='|')
        dw.writer.writerow(dw.fieldnames)
        dw.writerows(results)

def new_results(results):
    if len(results) == 0:
        return []

    if not os.path.exists('results.csv'):
        return results

    fields = results[0].keys()
    with open('results.csv', 'r') as f:
        reader = csv.DictReader(f, fieldnames=fields, delimiter='|')
        seen_urls = [row['url'] for row in reader]

    new_posts = []
    for post in results:
        if post['url'] not in seen_urls:
            new_posts.append(post)
    return new_posts



#def send_text(phone_number, msg):
#    fromaddr = "Craigslist Checker"
#    toaddrs = phone_number + "@txt.att.net"
#    msg = ("From: {0}\r\nTo: {1}\r\n\r\n{2}").format(fromaddr, toaddrs, msg)
#    server = smtplib.SMTP('smtp.gmail.com:587')
#    server.starttls()
#    server.login(config.email['username'], config.email['password'])
#    server.sendmail(fromaddr, toaddrs, msg)
#    server.quit()

def get_current_time():
    return format_time(datetime.now())

def format_time(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')

def utf8(string):
    return string.encode(encoding='UTF-8',errors='strict')

if __name__ == '__main__':
   
    TERM = "ikea chair"
    
    html = get_query_result(TERM)
    results = parse_results(html)
    
    # Send the SMS message if there are new results
    new_posts  = new_results(results)
    if len(new_posts) > 0:
        #message = "Hey - there are new Craigslist posts for: {0}".format(TERM.strip())
        #prgint "[{0}] There are new results - sending text message to {0}".format(get_current_time(), PHONE_NUMBER)
        #send_text(PHONE_NUMBER, message)
        write_results(results)
        new_posts = sorted(new_posts, lambda x,y: x['create_date'] > y['create_date'])
        for post in new_posts:
            print "{0:<20} {1:<30.30} {2:<5} {3:80}".format(\
                    format_time(post['create_date']), \
                    utf8(post['title']),\
                    post['price'],\
                    post['url'])
        print "{} new records".format(len(new_posts))
    else:
        print "no new records"
