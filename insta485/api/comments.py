"""REST API for comments."""
import flask
import insta485
import insta485.model
from insta485.api.helpers import get_auth_user

@insta485.app.route('/api/v1/comments/', methods=["POST"])
def create_comment():
    """Create a new comment based on the text in 
    the JSON body for the specified post id."""
    
    postid = flask.request.args.get("postid", default=0, type=int)
    text = flask.request.get_json()
    text = text['text']
    
    username = get_auth_user()
    # Check if user authorized
    if username is None:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection = insta485.model.get_db()
    # Check if postid is out of range
    post_cursor = connection.execute(
        """
        SELECT posts.postid
        FROM posts
        WHERE posts.postid = ?
        """,
        (postid,)
    )
    post = post_cursor.fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    connection.execute(
        """
        INSERT INTO comments (owner, postid, text)
        VALUES (?, ?, ?)
        """,
        (username, postid, text)
    )
    connection.commit()
    
    # Query database to return output
    comment_cursor = connection.execute(
        """
        SELECT
            comments.commentid,
            comments.owner,
            comments.text
        FROM comments
        WHERE comments.commentid = last_insert_rowid()
        """,
    ) 
    comment = comment_cursor.fetchone()
    
    lognameOwnsThis = None
    if comment['owner'] == username:
        lognameOwnsThis = True
    else:
        lognameOwnsThis = False
    
    comment_data = {
        "commentid": comment['commentid'],
        "lognameOwnsThis": lognameOwnsThis,
        "owner": comment['owner'],
        "ownerShowUrl": f"/users/{comment['owner']}/",
        "text": comment['text'],
        "url": f"/api/v1/comments/{comment['commentid']}/"
    }
    
    return flask.jsonify(comment_data), 201

@insta485.app.route('/api/v1/comments/<commentid>/', methods=["DELETE"])
def delete_comment(commentid):
    """Delete the comment based on the comment id."""

    username = get_auth_user()
    # Check if user authorized
    if username is None:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection = insta485.model.get_db()
    
    # Check if likeid does not exist
    comment_cursor = connection.execute(
        """
        SELECT
            comments.commentid,
            comments.owner
        FROM comments
        WHERE comments.commentid = ?
        """,
        (commentid,)
    )
    commented = comment_cursor.fetchone()
    if not commented:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if commented['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection.execute(
        """
        DELETE FROM comments
        WHERE commentid = ? AND owner = ?
        """,
        (commentid, username)
    )
    connection.commit()
    return '', 204