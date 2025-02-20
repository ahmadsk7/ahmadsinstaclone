"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.explore import show_explore
from insta485.views.uploads import uploads
from insta485.views.users import show_user
from insta485.views.users import show_followers
from insta485.views.users import show_following
from insta485.views.posts import show_post
from insta485.views.accounts import login
from insta485.views.accounts import create
from insta485.views.accounts import delete
from insta485.views.accounts import edit
from insta485.views.accounts import password
from insta485.views.accounts import auth
from insta485.views.likes import update_likes
from insta485.views.comments import update_comments
from insta485.views.following import update_following
from insta485.views.helpers import get_comments
from insta485.views.helpers import get_likes
from insta485.views.helpers import is_liked
# from insta485.views.accounts import logout
