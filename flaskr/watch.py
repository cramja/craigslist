from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
from cl.result_parser import get_and_parse

bp = Blueprint('watch', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    watches = db.execute(
        'select create_time, name, url, last_search_time, update_interval_minutes, id from watches where user_id = ? ' +
        ' order by create_time desc', (str(g.user["id"]))
    ).fetchall()
    return render_template('watch/index.html', watches=watches)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        update_interval_minutes = request.form['update_interval_minutes']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO watches (name, url, update_interval_minutes, last_search_time, user_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, url, update_interval_minutes, datetime.now(), g.user['id'])
            )
            db.commit()
            return redirect(url_for('watch.index'))

    return render_template('watch/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    watch = get_watch(id)

    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE watches SET name = ?, url = ?'
                ' WHERE id = ?',
                (name, url, id)
            )
            db.commit()
            return redirect(url_for('watch.index'))

    return render_template('watch/update.html', watch=watch)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_watch(id)
    db = get_db()
    db.execute('DELETE FROM watches WHERE id = ? AND user_id = ?', (id, g.user['id']))
    db.commit()
    return redirect(url_for('watch.index'))


@bp.route('/<int:id>/details', methods=('GET',))
@login_required
def get_details(id):
    def dict_from_row(row):
        return dict(zip(row.keys(), row))

    get_watch(id)  # does security check
    results = get_watch_results(id)
    args = []
    for result in results:
        d = dict_from_row(result)
        d['hours_ago'] = datetime.now() - datetime.strptime(d['post_time'], "%Y-%m-%d %H:%M:%S")
        args.append(d)

    return render_template('watch/details.html', results=args, id=id)


@bp.route('/<int:id>/update_search_results', methods=('GET',))
@login_required
def update_search_results(id):
    try:
        update_watch_results(id)
    except Exception as e:
        flash("failed to get watch url: {}. Try updating it...".format(e))
        return redirect(url_for('watch.update', id=id))
    return redirect(url_for('watch.get_details', id=id))


def get_watch(id, check_user=True):
    watch = get_db().execute(
        'SELECT w.id, name, url, create_time, update_interval_minutes, last_search_time, user_id, username'
        ' FROM watches w JOIN user u ON w.user_id = u.id'
        ' WHERE w.id = ?',
        (id,)
    ).fetchone()

    if watch is None:
        abort(404, "watch with id {0} does not exist.".format(id))

    if check_user and watch['user_id'] != g.user['id']:
        abort(403)

    return watch


def get_watch_results(id):
    results = get_db().execute(
        'SELECT id, post_time, cl_id, title, price, url'
        ' FROM watch_results WHERE watch_id = ? order by post_time desc',
        (id,)
    ).fetchall()

    return results


def update_watch_results(id):
    w = get_watch(id, False)
    results = get_and_parse(w['url'])
    db = get_db()
    for result in results:
        db.execute(
            "INSERT OR IGNORE INTO watch_results " +
            "(watch_id, post_time, query_time, cl_id, title, place, price, url) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (w['id'],
             result['create_time'],
             datetime.now(),
             result['id'],
             result['title'],
             result['place'],
             result['price'],
             result['url']))
    db.commit()
