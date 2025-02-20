"""Following."""
import flask
import flask.logging
import insta485
import insta485.model

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/following/", methods=["POST"])
def update_following():
    """Update following."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    operation = flask.request.form['operation']
    username = flask.request.form['username']
    logname = flask.session['username']
    target = flask.request.args.get('target')

    connection = insta485.model.get_db()

    if operation == "follow":
        # Check if already following
        follow_check_cursor = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, username)
        )

        already_following = follow_check_cursor.fetchone() is not None

        if already_following:
            flask.abort(409)

        connection.execute(
            """
            INSERT INTO following (username1, username2)
            VALUES (?, ?)
            """,
            (logname, username)
        )
        connection.commit()

    if operation == "unfollow":
        # Check if currently following
        unfollow_check_cursor = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, username)
        )

        currently_following = unfollow_check_cursor.fetchone() is not None

        if not currently_following:
            flask.abort(409)  # Not currently following the user

        connection.execute(
            """
            DELETE FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, username)
        )
        connection.commit()

    if target is None:
        target = flask.url_for('show_index')
    return flask.redirect(target)
