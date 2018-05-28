import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import open_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = open_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.get_user_by_name(username) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.create_user(username, generate_password_hash(password))
            db.commit_pending()
            flash("Successfully created user, " + username)
            return redirect(url_for('auth.login', u=username))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = open_db()
        error = None
        user = db.get_user_by_name(username)

        if user is None:
            error = 'Incorrect username or password'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password or password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = open_db().get_user_by_id(user_id)


def login_required(view):
    """
    Decorator to wrap any function which requires auth.
    :param view:
    :return: Redirect to login page if needed.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("The requested page requires authentication.", category='error')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view