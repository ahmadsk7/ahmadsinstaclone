"""Insta485 REST API."""

# TODO: ALL ROUTES NEED TO HAVE SOMETHING IMPORTED
from insta485.api.index import get_api_services
# from insta485.api.comments
# from insta485.api.likes
from insta485.api.posts import get_posts
from insta485.api.likes import create_like, delete_like
from insta485.api.comments import create_comment


