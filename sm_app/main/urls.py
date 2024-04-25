from django.urls import path, include
from main import main_views as main_v
from main import ajax_views as ajax_v
urlpatterns = [

    # Bace with no variable passing
    path('home/', main_v.home, name="home"),
    path('page/', main_v.page, name="page"),
    path('add/', main_v.add_post, name="add_post"),

    # Bace with variable passing
    path('error/<str:error>', main_v.error, name="error"),
    path('settings/<str:name>', main_v.config, name="settings"),
    path('profile/<str:name>', main_v.profile, name="profile"),
    path('posts/<int:post_id>', main_v.post_view, name="post_view"),

    # AJAX and jQuery paths
    path('page/liked/', ajax_v.liked, name="liked"),
    path('page/comment-liked/', ajax_v.comment_liked, name="comment_liked"),
    path('page/new_comment/', ajax_v.new_comment, name='new_comment'),
    path('page/new_reply/', ajax_v.new_reply, name='new_reply'),
]

