from django.urls import path
from main import main_views as main_v
from main.ajax_views import posts, post_creation, universal
urlpatterns = [

    # Bace with no variable passing
    path('home/', main_v.home, name="home"),
    path('add/', main_v.add_post, name="add_post"),

    # Bace with variable passing
    path('page/catch_up/<int:increment>', main_v.catch_up_page, name="catch_up_page"),
    path('page/<str:category>/<str:sub_category>/<int:increment>', main_v.page, name="page"),
    path('search/<str:q>/<int:post_increment>/<int:user_increment>/<int:catergory_increment>', main_v.search_results, name="search"),
    path('error/<str:error>', main_v.error, name="error"),
    path('settings/<str:name>', main_v.config, name="settings"),
    path('profile/<str:name>', main_v.profile, name="profile"),
    path('posts/<int:post_id>', main_v.post_view, name="post_view"),

    # AJAX views

    # for posts
    path('page/liked/', posts.liked, name="liked"),
    path('page/new-comment/', posts.new_comment, name="new_comment"),
    path('page/new_reply/', posts.new_reply, name="new_reply"),
    path('page/comment-liked/', posts.comment_liked, name="comment_liked"),
    path('page/scrolled-by/', posts.scrolled_by, name="scrolled_by"),
    path('page/load-posts/', posts.load_posts, name="load_posts"),
    path('page/save-location/', posts.save_location, name='save_location'),

    # for adding posts
    path('add/add-post/', post_creation.add_post, name="add_post"),

    # for universal functions
    path('universal/error/', universal.ajax_error, name="ajax_error"),
    path('universal/remove-notification/', universal.remove_notification, name='remove_notification'),
    path('universal/realtime-suggestions-manager/', universal.realtime_suggestions_manager, name='realtime_suggestions'),
    path('universal/check-depreciation-time/', universal.check_depreciation_time, name='check_depreciation_time'),
]

