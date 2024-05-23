from django.urls import path, include
from main import views as main_v
urlpatterns = [

    # Bace with no variable passing
    path('home/', main_v.home, name="home"),
    path('add/', main_v.add_post, name="add_post"),

    # Bace with variable passing
    path('error/<str:error>', main_v.error, name="error"),
    path('settings/<str:name>', main_v.config, name="settings"),
    path('profile/<str:name>', main_v.profile, name="profile"),
    path('posts/<int:post_id>', main_v.post_view, name="post_view"),
]

