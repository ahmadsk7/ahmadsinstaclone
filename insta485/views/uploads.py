"""Uploads."""
# import insta485
# from flask import session, send_from_directory, abort
# import flask
# import insta485.config
# import insta485.model

import flask
from flask import send_from_directory, abort
import insta485
import insta485.config
import insta485.model


# Uploads
@insta485.app.route('/uploads/<filename>')
def uploads(filename):
    """GET /uploads/<filename>."""
    if 'username' not in flask.session:
        flask.abort(403)

    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT 1
        FROM posts
        WHERE filename = ?
        OR EXISTS (
            SELECT 1
            FROM users
            WHERE filename = ?
        );
    """, (filename, filename))

    file_exists = cur.fetchone()
    cur.close()

    if not file_exists:
        abort(404)

    return send_from_directory(insta485.config.UPLOAD_FOLDER, filename)
