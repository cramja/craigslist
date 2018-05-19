import sqlite3 as sql
from datetime import datetime, timedelta

SQL = {
    "create_table_watches":
        """
create table if not exists watches (
    name text unique, 
    url text);
    """,

    "create_table_watch_results":
        """
create table if not exists watch_results (
    watch_name text, 
    post_time datetime, 
    query_time datetime, 
    cl_id int unique, 
    title text, 
    place text, 
    price int, 
    url text, 
    raw text, 
    foreign key(watch_name) references watches(name) on delete cascade);
    """,

    "insert_watch": """
insert into watches values (?,?);
    """,

    "insert_watch_result": """
insert into watch_results values (?,?,?,?,?,?,?,?,?)
    """,

    "delete_watch": """
delete from watches where name = ?;
    """,

    "get_watch_results_since": """
select post_time, title, price, place, url from watch_results where watch_name=? and post_time > ? order by post_time desc
"""
}

DB = "/tmp/.cl-sqlite.db"


class WatchDb:

    def __init__(self):
        self._initialize()

    def __del__(self):
        self.conn.close()

    def _initialize(self):
        self.conn = sql.connect(DB)
        self.conn.execute(SQL["create_table_watches"])
        self.conn.execute(SQL["create_table_watch_results"])
        self.conn.commit()
        self.conn.row_factory = sql.Row

    def create_watch(self, name, url):
        self.conn.execute(SQL["insert_watch"], (name, url))
        self.conn.commit()

    def delete_watch(self, name):
        self.conn.execute(SQL["delete_watch"], [name])
        self.conn.commit()

    def get_watch_result(self, name, id):
        cur = self.conn.cursor()
        cur = cur.execute("select * from watch_results where watch_name = ? and cl_id = ?", [name, id])
        return cur.fetchone()

    def create_watch_result(self, watch_name, post_time, id, title, place, price, url, raw):
        self.conn.execute(SQL["insert_watch_result"],
                          (watch_name, post_time, datetime.now(), id, title, place, price, url, raw))
        self.conn.commit()

    def get_watches(self):
        cur = self.conn.cursor()
        cur = cur.execute("select rowid, watches.* from watches")
        return cur.fetchall()

    def get_watch_results(self, watch_name, hours_since):
        cur = self.conn.cursor()
        cur = cur.execute(SQL["get_watch_results_since"], [watch_name, datetime.now() - timedelta(hours=hours_since)])
        return cur.fetchall()
