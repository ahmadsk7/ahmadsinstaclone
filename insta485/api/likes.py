"""REST API for likes."""
import flask
import insta485
import insta485.model
from insta485.api.helpers import get_auth_user

@insta485.app.route('/api/v1/likes/', methods=["POST"])
def create_like():
    """Create a new like for the specified post id."""
    postid = flask.request.args.get("postid", default=0, type=int)
    
    username = get_auth_user()
    # Check if user authorized
    if username is None:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403

    connection = insta485.model.get_db()

    # Query database to check if like already exists
    query = """
        SELECT
        1,
        likes.likeid
        FROM likes
        WHERE owner = ? AND postid = ?;
        """
    parameters = [username, postid]

    liked_cursor = connection.execute(query, parameters)
    liked = liked_cursor.fetchone()
    
    post_cursor = connection.execute(
        """
        SELECT
            posts.postid
        FROM posts
        WHERE posts.postid = ?
        """,
        (postid,)
    )
    post = post_cursor.fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if liked:
        return flask.jsonify({"likeid": liked['likeid'], "url": f"/api/v1/likes/{liked['likeid']}/"}), 200
    else:
        # Query database to create a like for a specific post
        connection.execute(
            """
            INSERT INTO likes (postid, owner)
            VALUES (?, ?)
            """,
            (postid, username)
        )
        created_cursor = connection.execute(query, parameters)
        created = created_cursor.fetchone()
        print(created)
        connection.commit()
        return flask.jsonify({"likeid": created['likeid'], "url": f"/api/v1/likes/{created['likeid']}/"}), 201

@insta485.app.route('/api/v1/likes/<likeid>/', methods=["DELETE"])
def delete_like(likeid):
    """Delete the like based on the like id."""
    
    username = get_auth_user()
    # Check if user authorized
    if username is None:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection = insta485.model.get_db()
    
    # Check if likeid does not exist
    liked_cursor = connection.execute(
        """
        SELECT
            likes.likeid,
            likes.owner
        FROM likes
        WHERE likes.likeid = ?
        """,
        (likeid,)
    )
    liked = liked_cursor.fetchone()
    if not liked:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if liked['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection.execute(
        """
        DELETE FROM likes
        WHERE likeid = ? AND owner = ?
        """,
        (likeid, username)
    )
    connection.commit()
    return '', 204
