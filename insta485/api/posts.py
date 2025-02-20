"""REST API for posts."""
import flask
import insta485
from insta485.api.helpers import get_auth_user, get_post_comments, get_posts_likes
import insta485.model

@insta485.app.route('/api/v1/posts/', methods=["GET"])
def get_posts():
  """Return the 10 newest posts."""

  # Query parameters
  size = flask.request.args.get("size", default=10, type=int)
  page = flask.request.args.get("page", default=0, type=int)
  postid_lte = flask.request.args.get("postid_lte", default=None, type=int)

  if page < 0 or size <= 0:
    return flask.jsonify({"message": "Bad Request", "status_code": 400}), 400

  # Retrieve username from basic auth or session
  username = get_auth_user()
  # Check if user authorized
  if username is None:
    return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403

  connection = insta485.model.get_db()
  # Initial query
  query = """
    SELECT posts.postid
    FROM posts
    JOIN users ON posts.owner = users.username
    WHERE (posts.owner = ? OR posts.owner IN (
      SELECT username2
      FROM following
      WHERE username1 = ?
    ))
  """
  parameters = [username, username]

  # Check if postid exists
  if postid_lte is not None:
      query += " AND posts.postid <= ?"
      parameters.append(postid_lte)
  else:
      # Get most recent postid
      post_cursor = connection.execute(
        """
        SELECT MAX(postid) as recent_postid
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE (posts.owner = ? OR posts.owner IN (
            SELECT username2
            FROM following
            WHERE username1 = ?
        ))
        """,
        (username, username)
      )
      recent_post = post_cursor.fetchone()

      if recent_post['recent_postid'] is not None:
          postid_lte = recent_post['recent_postid']
          query += " AND posts.postid <= ?"
          parameters.append(postid_lte)

  query += " ORDER BY posts.postid DESC LIMIT ? OFFSET ?"
  # Calc offset
  offset = page * size
  parameters.append(size)
  parameters.append(offset)

  # Execute entire query
  posts_cursor = connection.execute(query, parameters)
  posts = posts_cursor.fetchall()

  results = []
  for post in posts:
    results.append({
      "postid": post['postid'],
      "url": f"/api/v1/posts/{post['postid']}/"
    })

  next_url = None
  if len(posts) < size:
    next_url = ""
  else:
    next_url = f"/api/v1/posts/?size={size}&page={page + 1}"
    if postid_lte is not None:
      next_url += f"&postid_lte={postid_lte}"
    
  full_url = flask.request.url
  rel_url = full_url.split(flask.request.host_url, 1)[-1] 
  
  if not rel_url.startswith("/"):
      rel_url = "/" + rel_url
      
  context = {
    "next": next_url,
    "results": results,
    "url": rel_url
  }
  return flask.jsonify(**context), 200

@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """Return post on postid."""
    
    # Retrieve username from basic auth or session
    username = get_auth_user()
    # Check if user authorized
    if username is None:
      return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    
    connection = insta485.model.get_db()
    
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
    
    # Means that post id is out of range and our query returned nothing
    if post is None:
      return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    comments = get_post_comments(connection, username, postid_url_slug)
    
    likes = get_posts_likes(connection, username, postid_url_slug)
    
    timestamp = post['created']
    
    context = {
      "comments": comments,
      "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
      "created": timestamp,
      "imgUrl": f"/uploads/{post['filename']}",
      "likes": likes,
      "owner": post['owner'],
      "ownerImgUrl": f"/uploads/{post['user_filename']}",
      "ownerShowUrl": f"/users/{post['owner']}/",
      "postShowUrl": f"/posts/{postid_url_slug}/",
      "postid": postid_url_slug,
      "url": flask.request.path,
    }
    return flask.jsonify(**context)
