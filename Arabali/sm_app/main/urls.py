from django.urls import path, include
from main import views as main_v
urlpatterns = [
    path('home/', main_v.home, name="home"),
    path('page/', main_v.page, name="page"),
]
