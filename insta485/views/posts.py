"""Posts."""
import pathlib
import uuid

import flask
import flask.logging
import arrow

import insta485
import insta485.model
from insta485.views.helpers import get_comments, get_likes, is_liked


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Show post."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()

    # Query db for post using postid_url_slug
    logname = flask.session['username']
    post_cursor = connection.execute(
        """
        SELECT
            posts.postid,
            posts.filename,
            posts.owner,
            posts.created,
            users.filename AS user_filename
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.postid = ?
        """,
        (postid_url_slug,)
    )

    post = post_cursor.fetchone()

    comments = get_comments(connection, post['postid'])

    likes = get_likes(connection, post['postid'])

    # Check if user liked post or not
    liked = is_liked(connection, logname, post['postid'])

    user_liked_post = None
    if liked:
        user_liked_post = True
    elif not liked:
        user_liked_post = False

    timestamp = arrow.get(post['created']).humanize()
    post_data = {
        "logname": logname,
        "postid": postid_url_slug,
        "owner": post['owner'],
        "owner_img_url": post['user_filename'],
        "img_url": post['filename'],
        "timestamp": timestamp,
        "likes": likes['like_count'],
        "user_liked_post": user_liked_post,
        "comments": comments
    }

    context = {"post": post_data, "logname": logname}
    return flask.render_template("post.html", **context)


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/posts/", methods=["POST"])
def update_posts():
    """Update posts."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # LOGGER.debug("operation = %s", flask.request.form["operation"])
    # LOGGER.debug("postid = %s", flask.request.form["postid"])

    operation = flask.request.form['operation']
    target = flask.request.args.get('target')
    logname = flask.session['username']

    connection = insta485.model.get_db()

    LOGGER.debug("target = %s", target)

    # If operation is create
    if operation == "create":
        # Save the image file to disk

        # Unpack flask object
        fileobj = flask.request.files["file"]
        LOGGER.debug("fileobj = %s", fileobj.filename)

        # If a user tries to create a post with an empty file, then abort(400).
        if not fileobj or fileobj.filename == "":
            flask.abort(400)

        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            """
            INSERT INTO posts (filename, owner)
            VALUES (?, ?)
            """,
            (uuid_basename, logname)
        )
        connection.commit()

    # If operation is delete
    if operation == "delete":
        postid = flask.request.form['postid']
        post_cursor = connection.execute(
            """
            SELECT owner, filename
            FROM posts
            WHERE postid = ?
            """,
            (postid, )
        )
        post = post_cursor.fetchone()

        # If a user tries to delete a post that they do not own,
        # then abort(403).
        if post['owner'] != logname:
            flask.abort(403)

        # Delete the image file for postid from the filesystem.
        filepath = pathlib.Path(
            insta485.app.config["UPLOAD_FOLDER"]/post['filename']
                    )
        if filepath.exists():
            filepath.unlink()

        # Delete everything in the database related to this post.
        connection.execute(
            """
                DELETE FROM posts
                WHERE postid = ?
            """,
            (postid, )
        )
        connection.commit()

    # If the value of ?target is not set,
    # redirect to /users/<logname>/.

    if not target:
        return flask.redirect(
            flask.url_for("show_user", user_url_slug=logname)
        )
    return flask.redirect(target)

    # PITFALL: Do not call render_template()
