"""Accounts."""

import os
import pathlib
import uuid
import hashlib

import flask
import flask.logging
from flask import abort

import insta485

LOGGER = flask.logging.create_logger(insta485.app)


def hash_password(input_password, salt=None):
    """Hash password."""
    algorithm = 'sha512'
    if not salt:
        salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_password
    hash_obj.update(password_salted.encode('utf-8'))
    return "$".join([algorithm, salt, hash_obj.hexdigest()])


def fetch_user(connection, username):
    """Fetch user."""
    user_cursor = connection.execute(
        """
        SELECT username, password
        FROM users
        WHERE username = ?
        """, (username,))
    return user_cursor.fetchone()


def save_user_photo(file, upload_folder):
    """Save uploaded photo."""
    filename = file.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = upload_folder / uuid_basename
    file.save(path)
    return uuid_basename


@insta485.app.route("/accounts/", methods=["POST"])
def update_accounts():
    """Update accounts."""
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    operation = flask.request.form['operation']
    target = flask.request.args.get('target') or flask.url_for('show_index')
    connection = insta485.model.get_db()

    if operation == "login":
        return handle_login(connection, target)
    if operation == "create":
        return handle_create(connection, target)
    if operation == "delete":
        return handle_delete(connection, target)
    if operation == "edit_account":
        return handle_edit_account(connection, target)
    if operation == "update_password":
        return handle_update_password(connection, target)

    flask.abort(400)


def handle_login(connection, target):
    """Handle user login."""
    username = flask.request.form['username']
    user_password = flask.request.form['password']

    if not username or not user_password:
        flask.abort(400)

    user = fetch_user(connection, username)
    if not user or hash_password(
        user_password, user['password'].split('$')[1]
    ) != user['password']:
        flask.abort(403)

    flask.session['username'] = username
    return flask.redirect(target)


def handle_create(connection, target):
    """Handle account creation."""
    username = flask.request.form['username']
    user_password = flask.request.form['password']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    file = flask.request.files['file']

    if not all([username, user_password, fullname, email, file]):
        flask.abort(400)

    if fetch_user(connection, username):
        flask.abort(409)

    flask.session['username'] = username
    password_db_string = hash_password(user_password)
    uuid_basename = save_user_photo(file, insta485.app.config["UPLOAD_FOLDER"])

    connection.execute(
        """
        INSERT INTO users (username, password, fullname, email, filename)
        VALUES(?,?,?,?,?)
        """, (username, password_db_string, fullname, email, uuid_basename)
    )
    connection.commit()
    return flask.redirect(target)


def handle_delete(connection, target):
    """Handle account deletion."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']
    connection.execute("DELETE FROM users WHERE username = ?", (username,))
    connection.commit()
    flask.session.clear()
    return flask.redirect(target)


def handle_edit_account(connection, target):
    """Handle account editing."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    file = flask.request.files.get("file")

    if not fullname or not email:
        flask.abort(400)

    if file and file.filename:
        old_file = connection.execute(
            "SELECT filename FROM users WHERE username = ?", (username,)
        ).fetchone()['filename']
        uuid_basename = save_user_photo(
            file,
            insta485.app.config["UPLOAD_FOLDER"]
        )
        os.remove(insta485.app.config["UPLOAD_FOLDER"] / old_file)

        connection.execute(
            """
            UPDATE users
            SET filename = ?, fullname = ?, email = ?
            WHERE username = ?
            """, (uuid_basename, fullname, email, username)
        )
    else:
        connection.execute(
            """UPDATE users
            SET fullname = ?,
            email = ?
            WHERE username = ?""",
            (fullname, email, username)
        )

    connection.commit()
    return flask.redirect(target)


def handle_update_password(connection, target):
    """Handle password update."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']
    current_password = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']

    if not all([current_password, new_password1, new_password2]):
        flask.abort(400)

    stored_password = connection.execute(
        "SELECT password FROM users WHERE username = ?", (username,)
    ).fetchone()['password']

    if hash_password(
        current_password,
        stored_password.split('$')[1]
    ) != stored_password:
        flask.abort(403)
    if new_password1 != new_password2:
        flask.abort(401)

    new_password_hash = hash_password(new_password1)
    connection.execute(
        """UPDATE users
        SET password = ?
        WHERE username = ?
        """,
        (new_password_hash, username)
    )
    connection.commit()
    return flask.redirect(target)


@insta485.app.route('/accounts/login/', methods=['GET'])
def login():
    """Login GET."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template('login.html')


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout POST."""
    if 'username' in flask.session:
        flask.session.clear()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('login.html')


@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    """Create GET."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    """Delete GET."""
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session.get('username')
    return flask.render_template('delete.html', logname=username)


@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit():
    """Edit GET."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']
    connection = insta485.model.get_db()

    user_cursor = connection.execute(
        """
        SELECT fullname, email, filename
        FROM users
        WHERE username = ?
        """, (username,)
    )
    user = user_cursor.fetchone()

    return flask.render_template(
        'edit.html',
        logname=username,
        filename=user['filename'],
        fullname=user['fullname'],
        email=user['email']
    )


@insta485.app.route('/accounts/password/', methods=['GET'])
def password():
    """Password GET."""
    if 'username' not in flask.session:
        flask.abort(403)
    username = flask.session['username']
    return flask.render_template(
        'password.html',
        logname=username
    )


@insta485.app.route('/accounts/auth/', methods=['GET'])
def auth():
    """Auth GET."""
    if 'username' in flask.session:
        return '', 200
    abort(403)
