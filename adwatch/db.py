import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:

    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = dict_factory

    def init(self):
        with current_app.open_resource('schema.sql') as f:
            self.conn.executescript(f.read().decode('utf8'))

    def commit_pending(self):
        self.conn.commit()

    def get_user_by_name(self, name):
        return self.conn.execute('SELECT * FROM user WHERE username = ?', (name,)).fetchone()

    def get_user_by_id(self, id):
        return self.conn.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()

    def create_user(self, name, password_hash):
        self.conn.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (name, password_hash,))

    def get_watch(self, id):
        return self.conn.execute(
            'SELECT w.id, name, url, create_time, update_interval_minutes, last_search_time, user_id, username'
            ' FROM watches w JOIN user u ON w.user_id = u.id'
            ' WHERE w.id = ?',
            (id,)).fetchone()

    def get_watches_by_user(self, user_id):
        return self.conn.execute(
            'select create_time, name, url, last_search_time, ' +
            ' update_interval_minutes, id, round((julianday(datetime(\'now\')) - julianday(last_search_time)) * 1440.0,1) as time_since_minutes from watches ' +
            ' where user_id = ? order by create_time desc', (user_id,)
        ).fetchall()

    def get_pending_watches(self):
        return self.conn.execute("SELECT * FROM watches WHERE last_search_time IS NULL OR " +
                                 " (julianday(CURRENT_TIMESTAMP) - julianday(last_search_time)) * 1440.0 " +
                                 " > update_interval_minutes ").fetchall()

    def create_watch(self, name, url, user_id, update_interval_minutes=60):
        self.conn.execute(
            'INSERT INTO watches (name, url, update_interval_minutes, last_search_time, user_id)'
            ' VALUES (?, ?, ?, ?, ?)',
            (name, url, update_interval_minutes, datetime.now(), user_id,))

    def update_watch(self, id, name, url, update_interval_min):
        self.conn.execute(
            'UPDATE watches SET name = ?, url = ?, update_interval_minutes = ? WHERE id = ?',
            (name, url, update_interval_min, id,))

    def update_watch_last_search_time(self, id):
        self.conn.execute("UPDATE watches SET last_search_time = CURRENT_TIMESTAMP WHERE id = ?", (id,))

    def delete_watch(self, id):
        self.conn.execute('DELETE FROM watches WHERE id = ?', (id,))

    def get_watch_results(self, id):
        return self.conn.execute(
            'SELECT id, post_time, cl_id, title, price, url'
            ' FROM watch_results WHERE watch_id = ? order by post_time desc',
            (id,)
        ).fetchall()

    def create_watch_result(self, watch_id, create_time, cl_id, title, place, price, url):
        self.conn.execute(
            "INSERT OR IGNORE INTO watch_results " +
            "(watch_id, post_time, query_time, cl_id, title, place, price, url) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (watch_id,
             create_time,
             datetime.now(),
             cl_id,
             title,
             place,
             price,
             url,))

    def __del__(self):
        self.conn.close()


def open_db():
    if 'db' not in g:
        g.db = Database(sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES))

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        del db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create new tables, clear data."""
    db = open_db()
    db.init()
    click.echo('Reset the database at {}'.format(current_app.config['DATABASE']))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
