"""Comments."""
import flask
import flask.logging
import insta485
import insta485.model

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/comments/", methods=["POST"])
def update_comments():
    """Update comments."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    operation = flask.request.form['operation']
    logname = flask.session['username']
    target = flask.request.args.get('target')

    connection = insta485.model.get_db()

    if operation == "create":
        postid = flask.request.form['postid']
        text = flask.request.form['text']
        # Empty comment
        if not text:
            flask.abort(400)

        connection.execute(
            """
            INSERT
            INTO comments (owner, postid, text)
            VALUES (?, ?, ?)
            """,
            (logname, postid, text)
        )
        connection.commit()

    if operation == "delete":
        commentid = flask.request.form['commentid']
        comment_cursor = connection.execute(
            """
            SELECT owner
            FROM comments
            WHERE commentid = ?
            """,
            (commentid,)
        )

        comment = comment_cursor.fetchone()

        if comment['owner'] != logname:
            flask.abort(403)

        connection.execute(
            """
            DELETE FROM comments
            WHERE commentid = ?
            """,
            (commentid,)
        )
        connection.commit()

    if target is None:
        target = flask.url_for('show_index')
    return flask.redirect(target)
