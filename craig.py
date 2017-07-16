#!/usr/bin/env python
from requests import request as req
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3 as sql
import os

# Craigslist search URL
# BASE_URL = ('http://chicago.craigslist.org/search/'
#            '?sort=rel&areaID=11&subAreaID=&query={0}&catAbb=sss')
BASE_URL = ('https://sfbay.craigslist.org/search/{}?query={}&sort=date&srchType=T&search_distance=10&postal=94025')
DEFAULTS = {
    "params": "&sort=date&srchType=T&search_distance=10&postal=94025",
    "db_name": "craigslist.db"
}

DEBUG = True
SCHEMA = ["create table query (name text unique, category text, terms text, params text, status int);",
          "create table results (query_name text, post_time datetime, query_time datetime, cl_id int unique, title text, place text, price int, url text, raw text, foreign key(query_name) references query(name));"]


def dprint(msg, *args):
    if DEBUG:
        print(msg.format(*args))


def get_conn(name):
    if not os.path.isfile(name):
        conn = sql.connect(name)
        dprint("db {} not found, creating db", name)
        for tbl in SCHEMA:
            conn.execute(tbl)
        conn.commit()
        return conn
    conn = sql.connect(name)
    return conn


def add_query(conn, name, category, terms):
    try:
        conn.execute("insert into query values (?,?,?,?,?);", (name, category, terms, DEFAULTS['params'], "1"))
        conn.commit()
    except sql.IntegrityError as e:
        print "query with name {} already exists, not creating".format(name)


def add_result(conn, query_name, post_time, id, title, place, price, url, raw):
    try:
        conn.execute("insert into results values (?,?,?,?,?,?,?,?,?);",
                     (query_name, post_time, datetime.now(), id, title, place, price, url, raw))
        conn.commit()
        return 1
    except sql.IntegrityError as e:
        return 0



def active_queries(conn):
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur = cur.execute("select rowid, query.* from query where query.status=?", "1")
    queries = cur.fetchall()
    return queries


def do_active(conn):
    queries = active_queries(conn)
    for q in queries:
        html_result = get_query_result(q['category'], q['terms'])
        results = parse_results(html_result)
        dprint("parsed {} results for {}", len(results), q['terms'])
        added = 0
        for r in results:
            added += add_result(conn, q['name'], r['create_date'], r['id'], r['title'], r['place'], r['price'], r['url'], html_result)
        print "for query {}, {} results added".format(q['name'], added)


def get_query_result(category, search_term):
    search_term = search_term.strip().replace(' ', '+')
    search_url = BASE_URL.format(category, search_term)
    result = req("get", search_url)
    if result.status_code == 200:
        return result.content.decode('utf-8', 'ignore')
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
            price = int(price[1:])
        except:
            price = -1
        timestamp = row.find('time', class_='result-date').get('datetime')
        id = int(row.p.a['data-id'])
        place = row.find('span', class_='result-hood').get_text()[2:-1]
        create_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        title = row.find_all('a')[1].get_text()
        results.append({'url': url, 'id':id, 'create_date': create_date, 'title': title, 'price': price, 'place': place})
    return results


def get_current_time():
    return format_time(datetime.now())


def format_time(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')


def utf8(string):
    return string.encode(encoding='UTF-8', errors='strict')


def main():
    my_queries = [("i_chair", 'fua', "ikea chair"), ("desk", "fua", "standing desk"), ("corolla", "cta", "toyota corolla manual"),]
    conn = get_conn(DEFAULTS['db_name'])
    for q in my_queries:
        add_query(conn, q[0], q[1], q[2])

    do_active(conn)

    before = 1
    print "results from the {} day".format(before)
    for q in my_queries:
        print q[0]
        results = conn.execute("select post_time, title, price, place, url from results where query_name=? and post_time > ? order by post_time desc;", [q[0], datetime.now() - timedelta(days=before)]).fetchall()
        for row in results:
            print row


if __name__ == '__main__':
    main()
