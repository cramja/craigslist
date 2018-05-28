from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from adwatch.auth import login_required
from adwatch.db import open_db
from adwatch.worker import update_watch_results
from datetime import datetime

bp = Blueprint('watch', __name__)


@bp.route('/')
@login_required
def index():
    db = open_db()
    return render_template('watch/index.html',
                           watches=db.get_watches_by_user(g.user['id']))


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
            db = open_db()
            db.create_watch(name, url, g.user['id'], update_interval_minutes)
            db.commit_pending()

            return redirect(url_for('watch.index'))

    return render_template('watch/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    watch = get_watch(id)

    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        update_interval_min = int(request.form['url'])
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = open_db()
            db.update_watch(id, name, url, update_interval_min)
            db.commit_pending()
            return redirect(url_for('watch.index'))

    return render_template('watch/update.html', watch=watch)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_watch(id)
    db = open_db()
    db.delete_watch(id)
    db.commit_pending()
    return redirect(url_for('watch.index'))


@bp.route('/<int:id>/details', methods=('GET',))
@login_required
def get_details(id):
    get_watch(id)  # does security check
    results = get_watch_results(id)
    for result in results:
        result['hours_ago'] = datetime.now() - result['post_time']

    return render_template('watch/details.html', results=results, id=id)


@bp.route('/<int:id>/update_search_results', methods=('GET',))
@login_required
def update_search_results(id):
    try:
        update_watch_results(open_db(), id)
    except Exception as e:
        flash("failed to get watch url: {}. Try updating it...".format(e))
        return redirect(url_for('watch.update', id=id))
    flash("update successful")
    return redirect(url_for('watch.get_details', id=id))


def get_watch(id, check_user=True):
    watch = open_db().get_watch(id)

    if watch is None:
        abort(404, "watch with id {0} does not exist.".format(id))

    if check_user and watch['user_id'] != g.user['id']:
        abort(403)

    return watch


def get_watch_results(id):
    return open_db().get_watch_results(id)

