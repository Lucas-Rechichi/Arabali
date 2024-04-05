from django.urls import path, include
from main import views as main_v
urlpatterns = [
    path('home/', main_v.home, name="home"),
    path('page/', main_v.page, name="page"),
    path('add/', main_v.add_post, name="add_post"),
    path('error/<str:error>', main_v.error, name="error"),
    path('edit/<str:name>', main_v.edit_profile, name="edit_profile"),
    path('page/liked/', main_v.liked, name="liked"),
    path('profile/<str:name>', main_v.profile, name="profile"),
    path('posts/<int:post_id>', main_v.post_view, name="post_view"),
]


