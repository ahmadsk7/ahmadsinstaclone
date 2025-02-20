"""Explore."""
import flask
import insta485

# Uploads


@insta485.app.route('/explore/')
def show_explore():
    """Show explore."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    logname = flask.session['username']
    cur = connection.execute(
        """
        SELECT
            users.username,
            users.filename
        FROM users
        WHERE users.username != ?
        AND users.username NOT IN (
            SELECT following.username2
            FROM following
            WHERE following.username1 = ?
        )
        """,
        (logname, logname)
    )

    users = cur.fetchall()

    users_data = {
        "logname": logname,
        "not_following": users
    }

    # Add database info to context
    context = {"users": users_data, "logname": logname}
    return flask.render_template("explore.html", **context)
