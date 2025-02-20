"""Helper functions."""


def get_comments(connection, post_id):
    """Get Comments."""
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
        (post_id,)
    )
    return comments_cursor.fetchall()


def get_likes(connection, post_id):
    """Get Likes for each post."""
    likes_cursor = connection.execute(
        """
        SELECT
            COUNT(likes.likeid) as like_count
        FROM likes
        WHERE likes.postid = ?;
        """,
        (post_id,)
    )
    return likes_cursor.fetchone()


def is_liked(connection, owner, post_id):
    """Check if post is liked by user."""
    liked_cursor = connection.execute(
        """
        SELECT
        1
        FROM likes
        WHERE owner = ? AND postid = ?;
        """,
        (owner, post_id)
    )
    return liked_cursor.fetchone()
