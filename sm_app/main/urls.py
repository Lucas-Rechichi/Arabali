from django.urls import path, include
from main import main_views as main_v
from main import ajax_views as ajax_v
urlpatterns = [

    # Bace with no variable passing
    path('home/', main_v.home, name="home"),
    path('add/', main_v.add_post, name="add_post"),

    # Bace with variable passing
    path('page/catch_up/<int:increment>', main_v.catch_up_page, name="catch_up_page"),
    path('page/<str:catagory>/<int:increment>', main_v.page, name="page"),
    path('search/<str:q>/<int:post_increment>/<int:user_increment>/<int:catergory_increment>', main_v.search_results, name="search"),
    path('error/<str:error>', main_v.error, name="error"),
    path('settings/<str:name>', main_v.config, name="settings"),
    path('profile/<str:name>', main_v.profile, name="profile"),
    path('posts/<int:post_id>', main_v.post_view, name="post_view"),

    # AJAX views
    path('page/liked/', ajax_v.liked, name="liked"),
    path('page/new_comment/', ajax_v.new_comment, name="new_comment"),
    path('page/new_reply/', ajax_v.new_reply, name="new_reply"),
    path('page/comment_liked/', ajax_v.comment_liked, name="comment_liked"),
    path('page/scrolled_by/', ajax_v.scrolled_by, name="scrolled_by"),
    path('page/error/', ajax_v.ajax_error, name="ajax_error"),
    path('page/save_location/', ajax_v.save_location, name='save_location'),
]

