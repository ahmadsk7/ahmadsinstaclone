"""Users."""
import flask
import insta485
import insta485.model


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Show user."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Connect to db
    connection = insta485.model.get_db()

    user_cursor = connection.execute(
        """
        SELECT
            users.username,
            users.fullname,
            users.filename
        FROM users
        WHERE users.username = ?
        """,
        (user_url_slug, )
    )

    user = user_cursor.fetchone()

    # ABORT 404 IF USER_URL_SLUG DOESNT EXIST IN DB
    if user is None:
        flask.abort(404)

    posts_cursor = connection.execute(
        """
        SELECT
            posts.postid,
            posts.filename
        FROM posts
        WHERE posts.owner = ?
        """,
        (user_url_slug, )
    )

    posts = posts_cursor.fetchall()

    follow_cursor = connection.execute(
        """
        SELECT
            username1,
            username2
        FROM following
        WHERE username1 = ? OR username2 = ?
        """,
        (flask.session['username'], user_url_slug)
    )

    follow = follow_cursor.fetchall()

    following = 0
    followers = 0

    followers_cursor = connection.execute(
        """
        SELECT username2
        FROM following
        WHERE username2 = ?
        """,
        (user_url_slug,)
    )

    for _ in followers_cursor:
        followers += 1

    following_cursor = connection.execute(
        """
        SELECT username1
        FROM following
        WHERE username1 = ?
        """,
        (user_url_slug,)
    )

    for _ in following_cursor:
        following += 1

    user_data = {
        "logname": flask.session['username'],
        "username": user_url_slug,
        "fullname": user['fullname'],
        "filename": user['filename'],
        "posts": posts,
        "followers": followers,
        "following": following,
        "total_posts": len(posts),
        "logname_follows_username": any(
            f['username1'] == flask.session['username']
            and f['username2'] == user_url_slug
            for f in follow
        )
    }

    # Return as context
    context = {"user": user_data, "logname": flask.session['username']}
    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Show followers."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    followers_cursor = connection.execute(
        """
        SELECT
            users.username,
            users.filename
        FROM following
        JOIN users ON users.username = following.username1
        WHERE
            following.username2 = ?
        """,
        (user_url_slug,)
    )

    user_cursor = connection.execute(
        """
        SELECT
            users.username,
            users.fullname,
            users.filename
        FROM users
        WHERE users.username = ?
        """,
        (user_url_slug, )
    )

    user = user_cursor.fetchone()
    # ABORT 404 IF USER_URL_SLUG DOESNT EXIST IN DB
    if user is None:
        flask.abort(404)

    followers = followers_cursor.fetchall()
    followers_data = []

    for follower in followers:
        follow = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ?
            AND username2 = ?
            """,
            (flask.session['username'], follower['username'])
        )
        followers_data.append({
            "logname": flask.session['username'],
            "username": follower['username'],
            "user_img_url": follower['filename'],
            "logname_follows_username": follow.fetchone() is not None,
        })

    context = {
        "followers": followers_data,
        "logname": flask.session['username']
    }
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Show following."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    following_cursor = connection.execute(
        """
            SELECT
                users.username,
                users.filename
            FROM following
            JOIN users ON users.username = following.username2
            WHERE
                following.username1 = ?
        """,
        (user_url_slug,)
    )

    user_cursor = connection.execute(
        """
        SELECT
            users.username,
            users.fullname,
            users.filename
        FROM users
        WHERE users.username = ?
        """,
        (user_url_slug, )
    )

    user = user_cursor.fetchone()
    # ABORT 404 IF USER_URL_SLUG DOESNT EXIST IN DB
    if user is None:
        flask.abort(404)

    following = following_cursor.fetchall()
    following_data = []

    for follow in following:
        follow_check = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ?
            AND username2 = ?
            """,
            (flask.session['username'], follow['username'])
        )
        following_data.append({
            "logname": flask.session['username'],
            "username": follow['username'],
            "user_img_url": follow['filename'],
            "logname_follows_username": follow_check.fetchone() is not None,
        })

    context = {
        "following": following_data,
        "logname": flask.session['username']
    }
    return flask.render_template("following.html", **context)
