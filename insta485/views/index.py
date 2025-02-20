"""Index."""
import flask
import arrow
import insta485
import insta485.model
from insta485.views.helpers import get_comments, get_likes, is_liked


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    # Connect to database
    connection = insta485.model.get_db()
    # Query database for posts and comments
    logname = flask.session['username']

    posts_cursor = connection.execute(
        """
            SELECT
                posts.postid,
                posts.filename,
                posts.owner,
                posts.created,
                users.filename AS user_filename
            FROM posts
            JOIN users ON posts.owner = users.username
            WHERE posts.owner = ?
                OR posts.owner IN (
                    SELECT username2
                    FROM following
                    WHERE username1 = ?
                )
            ORDER BY posts.postid DESC;
        """,
        (logname, logname)
    )

    posts = posts_cursor.fetchall()

    posts_data = []

    # loop through posts and for each post,
    # throw in the comment and likes
    for post in posts:
        # Get comments for each post
        comments = get_comments(connection, post['postid'])

        # Get each like count for each post
        likes = get_likes(connection, post['postid'])

        # Check if user liked post or not
        liked = is_liked(connection, logname, post['postid'])

        user_liked_post = None
        if liked:
            user_liked_post = True
        elif not liked:
            user_liked_post = False

        # Add post data with the comments and likes
        timestamp = arrow.get(post['created']).humanize()
        posts_data.append({
            "logname": logname,
            "postid": post['postid'],
            "filename": post['filename'],
            "owner": post['owner'],
            "created": timestamp,
            "comments": comments,
            "likes": likes['like_count'],
            "user_liked_post": user_liked_post,
            "user_filename": post['user_filename']
        })

    context = {
        "posts": posts_data,
        "logname": logname
    }
    return flask.render_template("index.html", **context)
