"""REST API for returning a list of services possible."""
import flask
import insta485


@insta485.app.route('/api/v1/')
def get_api_services():
    """Return API resource URLs."""

    context = {
        "posts": "/api/v1/posts/",
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)