"""Helper functions."""
import insta485
import insta485.model
import hashlib
import flask

def get_auth_user():
    """Check basic auth and session for user auth."""
    username = None

    # Check basic auth
    if flask.request.authorization:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']

        # Auth via basic auth
        if is_authenticated(username, password):
            return username 
        else:
            username = None

    # Check session
    if username is None and 'username' in flask.session:
        username = flask.session['username']

    return username 


def is_authenticated(inputted_username, inputted_password):
    """Check if user is authenicated (db)."""
    connection = insta485.model.get_db()

    # Query database for the stored password
    password_cursor = connection.execute(
        """
        SELECT password 
        FROM users 
        WHERE username = ?
        """, (inputted_username,)
    )

    # Get stored password from database
    stored_password = password_cursor.fetchone()
    # Get salt from stored password
    salt = stored_password['password'].split('$')[1]
    # Hash the inputted basic auth password
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    salted_password = salt + inputted_password
    hash_obj.update(salted_password.encode('utf-8'))
    hashed_password = "$".join([algorithm, salt, hash_obj.hexdigest()])

    user_cursor = connection.execute(
        """
        SELECT
            username,
            password
        FROM users
        WHERE users.username = ?
        AND users.password = ?
        """,
        (inputted_username, hashed_password)
    )

    user = user_cursor.fetchone()

    if user is None:
        return False
    else:
        return True
    
    
def get_post_comments(connection, user, postid_url_slug):
    comments_cursor = connection.execute(
        """
        SELECT
            comments.commentid,
            comments.owner,
            comments.postid,
            comments.text,
            comments.created
        FROM comments
        WHERE comments.postid = ?
        ORDER BY comments.created ASC;
        """,
        (postid_url_slug,)
    )
    
    
    comments = comments_cursor.fetchall()
    comments_data = []
    
    lognameOwnsThis = False
    
    for comment in comments:
        if comment['owner'] == user:
            lognameOwnsThis = True
        else:
            lognameOwnsThis = False
        comments_data.append({
            "commentid": comment['commentid'],
            "lognameOwnsThis": lognameOwnsThis,
            "owner": comment['owner'],
            "ownerShowUrl": f"/users/{comment['owner']}/",
            "text": comment['text'],
            "url": f"/api/v1/comments/{comment['commentid']}/"
        })
    
    return comments_data


def get_posts_likes(connection, user, postid_url_slug):
    likes_cursor = connection.execute(
        """
        SELECT
            COUNT(likes.likeid) as like_count,
            likes.likeid
        FROM likes
        WHERE likes.postid = ?;
        """,
        (postid_url_slug,)
    )
    likes = likes_cursor.fetchone()
    
    liked_cursor = connection.execute(
        """
        SELECT
        1
        FROM likes
        WHERE owner = ? AND postid = ?;
        """,
        (user, postid_url_slug)
    )
    
    liked = liked_cursor.fetchone()
    
    lognameLikesThis = None
    if liked:
        lognameLikesThis = True
    else:
        lognameLikesThis = False
    
    url = None
    if likes['likeid'] is not None:
        url = f"/api/v1/likes/{likes['likeid']}/"
    
    likes_data = {
        "lognameLikesThis": lognameLikesThis,
        "numLikes": likes['like_count'],
        "url": url,
    } 
    return likes_data