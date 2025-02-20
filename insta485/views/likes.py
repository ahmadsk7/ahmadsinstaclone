"""Likes."""
import flask
import flask.logging
import insta485
import insta485.model

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Update likes."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # LOGGER.debug("operation = %s", flask.request.form["operation"])
    # LOGGER.debug("postid = %s", flask.request.form["postid"])

    operation = flask.request.form['operation']
    postid = flask.request.form['postid']
    target = flask.request.args.get('target')
    logname = flask.session['username']
    # logname = flask.session.get('logname')
    # #Temp placeholder for when session is set up

    # Update the database

    connection = insta485.model.get_db()
    likes_cursor = connection.execute(
            """
            SELECT
            1
            FROM likes
            WHERE owner = ? AND postid = ?
            """,
            (logname, postid)
        )

    liked = likes_cursor.fetchone() is not None
    if operation == "like":

        if liked:
            flask.abort(409)
        else:
            connection.execute(
                """
                INSERT
                INTO likes (owner, postid)
                VALUES (?, ?)
                """,
                (logname, postid)
            )

            connection.commit()
        print(postid)

    if operation == "unlike":

        if not liked:
            flask.abort(409)
        else:
            connection.execute(
                """
                    DELETE
                    FROM likes
                    WHERE owner = ? AND postid = ?
                """,
                (logname, postid)
            )
        print(postid)

    if target is None:
        target = flask.url_for('show_index')
    return flask.redirect(target)
